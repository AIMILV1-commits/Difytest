"""
Pydantic models for request/response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., description="User's question", min_length=1)
    phone: str = Field(..., description="User's phone number", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    answer: str = Field(..., description="Response from the flow")
    intent: Optional[str] = Field(None, description="Classified intent")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class UserData(BaseModel):
    """User data from external API"""
    id: int = 0
    phone: str = ""
    name: str = ""
    empresa: str = ""
    cb_intent: str = ""


class IntentClassification(BaseModel):
    """Intent classification result"""
    intent: Literal["saudacao", "informacoes", "atendimento", "reclamacao", "elogio", "outros"]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
