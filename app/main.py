"""
EcoDrive Query API - Main FastAPI Application
"""
import logging
import uuid
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.models.schemas import QueryRequest, QueryResponse, HealthResponse
from app.services.external_api import ExternalAPIService
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting EcoDrive Query API...")
    yield
    logger.info("Shutting down EcoDrive Query API...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
external_api = ExternalAPIService()
llm_service = LLMService()
rag_service = RAGService()

# In-memory conversation storage (for demo - use Redis/DB in production)
conversations: Dict[str, List[Dict]] = {}


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.API_VERSION
    )


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user query through the EcoDrive flow

    This endpoint:
    1. Fetches user data by phone
    2. Classifies the query intent
    3. Routes to appropriate LLM handler
    4. Returns the generated response

    Args:
        request: QueryRequest with query and phone

    Returns:
        QueryResponse with answer and metadata
    """
    try:
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Get conversation history
        history = conversations.get(conversation_id, [])

        logger.info(f"Processing query for conversation {conversation_id}: {request.query[:50]}...")

        # Step 1: Fetch user data by phone
        user_data = await external_api.get_user_by_phone(request.phone)
        logger.info(f"User data retrieved: {user_data.name or 'Unknown'}")

        # Step 2: Classify intent
        intent = await llm_service.classify_intent(request.query, history)
        logger.info(f"Intent classified: {intent}")

        # Step 3: Route based on intent and generate response
        answer = ""

        if intent == "saudacao":
            # Greeting flow
            answer = await llm_service.generate_greeting(
                request.query,
                user_data.name,
                history
            )

        elif intent == "informacoes":
            # Information flow with RAG
            # Step 3a: Improve query for RAG
            improved_query = await llm_service.improve_query_for_rag(
                request.query,
                history
            )
            logger.info(f"Improved query for RAG: {improved_query}")

            # Step 3b: Retrieve context from knowledge base
            context = await rag_service.retrieve_context(improved_query)

            # Step 3c: Generate RAG response
            answer = await rag_service.generate_rag_response(
                request.query,
                context,
                history
            )

        elif intent in ["atendimento", "reclamacao"]:
            # Customer service flow
            answer = await llm_service.generate_attendance_response(
                request.query,
                history
            )

            # Notify Chatwoot (background task in production)
            await external_api.notify_chatwoot_label(conversation_id)

        elif intent == "elogio":
            # Praise flow
            answer = await llm_service.generate_praise_response(
                request.query,
                history
            )

        else:  # "outros"
            # Other/unclassified flow
            answer = await llm_service.generate_other_response(
                request.query,
                history
            )

        # Step 4: Update conversation history
        history.append({"role": "user", "content": request.query})
        history.append({"role": "assistant", "content": answer})
        conversations[conversation_id] = history

        logger.info(f"Response generated successfully for conversation {conversation_id}")

        return QueryResponse(
            answer=answer,
            intent=intent,
            conversation_id=conversation_id
        )

    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@app.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation history"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
