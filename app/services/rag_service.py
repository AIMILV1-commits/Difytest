"""
RAG (Retrieval-Augmented Generation) Service
"""
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI
import cohere
from app.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG operations with knowledge base"""

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.cohere_client = None
        if settings.COHERE_API_KEY:
            self.cohere_client = cohere.AsyncClient(api_key=settings.COHERE_API_KEY)

        # Parse dataset IDs from comma-separated string
        self.dataset_ids = [
            ds.strip() for ds in settings.DATASET_IDS.split(",") if ds.strip()
        ] if settings.DATASET_IDS else []

    async def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant context from knowledge base

        Note: This is a simplified version. In production, you would:
        1. Embed the query using OpenAI embeddings
        2. Search your vector database (Pinecone, Weaviate, etc.)
        3. Optionally rerank results using Cohere
        4. Return formatted context

        Args:
            query: Search query
            top_k: Number of results to retrieve

        Returns:
            Formatted context string
        """
        # TODO: Implement actual vector database retrieval
        # For now, return empty context - you need to integrate with your KB
        logger.warning("Knowledge base retrieval not implemented - using placeholder")

        # Placeholder implementation
        context = f"""
[NOTA: Esta é uma implementação placeholder. Integre com seu banco de dados vetorial]

Query: {query}

Para implementar a busca real:
1. Use OpenAI embeddings para vetorizar a query
2. Busque no seu vector store (Pinecone, Weaviate, ChromaDB, etc.)
3. Opcionalmente, use Cohere rerank para melhorar os resultados
4. Retorne os documentos relevantes

Datasets configurados: {len(self.dataset_ids)}
"""
        return context

    async def generate_rag_response(self, query: str, context: str, history: List[Dict] = None) -> str:
        """
        Generate response using RAG with retrieved context

        Args:
            query: User's query
            context: Retrieved context from knowledge base
            history: Conversation history

        Returns:
            Generated response
        """
        system_prompt = f"""<persona>
Você é o Rodrigo, assistente da EcoDrive, uma empresa especializada na venda de scooters elétricas. Sua missão é atender os clientes de forma simpática, útil e organizada, criando uma experiência agradável e eficiente no atendimento via WhatsApp.

  Seu estilo de comunicação deve ser:
  - Informal, simpático e acessível.
  - Adaptado ao canal (WhatsApp), com uso opcional de emojis para tornar a resposta mais amigável.
  - Claro e organizado, destacando informações com *itálico* e **negrito** quando necessário.
</persona>

<objetivo>
  Gerar a melhor resposta possível com base na pergunta do cliente (query) e nas informações adicionais disponíveis (contexto). A resposta será enviada via WhatsApp, e por isso deve ser clara, bem formatada e adaptada ao canal.
</objetivo>

<entrada>
  Você receberá os seguintes dados:

  [query]
  {{query}}
  [/query]

  [context]
  {{context}}
  [/context]
</entrada>

<instrucoes_de_formato>
  1. A resposta será enviada via WhatsApp, portanto:
     - Utilize bullets (`•`) para organizar listas de forma clara e fácil de ler.
     - Use emojis apenas se forem úteis para o tom da conversa ou para facilitar a leitura.
     - Destaque informações importantes usando **negrito** ou *itálico* — evite símbolos de Markdown como `*` ou `#`.
     - Se for necessário enviar links:
       • Links de imagens devem ser destacados separadamente, com breve explicação.
       • Links comuns devem ser posicionados de forma natural no texto e com contexto claro.
     - Evite formatações HTML ou códigos técnicos.

  2. Adapte o nível de detalhamento de acordo com o contexto recebido. Se houver muitas informações relevantes no contexto, organize-as bem para não sobrecarregar o cliente.
- Priorize envio de imagens quando estiverem no contexto
- Priorize envio de links quando estiverem no contexto

  3. Seja direto, útil e acolhedor. Evite respostas genéricas.

  4. Quando receber links no contexto mantenha-os de forma organizada
</instrucoes_de_formato>

<instrucoes_de_idioma>
  - Detecte automaticamente o idioma da mensagem recebida.
  - Responda no mesmo idioma detectado.
  - Se não for possível detectar o idioma, responda em espanhol chileno.
</instrucoes_de_idioma>

<saida_esperada>
  Gere **apenas a resposta final a ser enviada ao cliente**, seguindo todas as instruções acima.
</saida_esperada>

<nao_fazer>
* Não diga que não pode enviar imagens diretamente
</nao_fazer>
<nao_fazer>
- não forneça e nem responda com informações que não estejam neste prompt
</nao_fazer>
<nao_fazer>
- não mude a notação monetária, use a moeda que receber em contexto
</nao_fazer>"""

        messages = history or []
        messages.append({"role": "user", "content": query})

        # Replace placeholders in system prompt
        system_prompt_filled = system_prompt.replace("{{query}}", query).replace("{{context}}", context)

        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL_RAG,
                messages=[
                    {"role": "system", "content": system_prompt_filled},
                    *messages
                ],
                temperature=settings.OPENAI_TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating RAG response: {e}")
            return "Disculpa, tuve un problema al procesar tu consulta. ¿Podrías intentarlo nuevamente? 😊"
