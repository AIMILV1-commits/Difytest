"""
Service for LLM interactions using OpenAI
"""
import json
import logging
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM operations"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def classify_intent(self, query: str, history: List[Dict] = None) -> str:
        """
        Classify user intent from query

        Args:
            query: User's query
            history: Conversation history

        Returns:
            Intent classification (saudacao, informacoes, atendimento, reclamacao, elogio, outros)
        """
        system_prompt = """<task>
Você é um assistente de vendas especializado da EcoDrive, responsável por analisar e classificar a intenção do cliente com base na query atual e no histórico de conversa.
</task>

<context>
A EcoDrive é uma empresa de mobilidade urbana que vende scooters, skates, patinetes e equipamentos relacionados. Você deve classificar a intenção do cliente para roteamento adequado.
</context>

<input_instructions>
1. Analise cuidadosamente a query do usuário:
   <query>{query}</query>

2. Considere também o histórico completo da conversa para contexto.

3. A query pode estar em qualquer idioma - você deve processá-la corretamente independentemente do idioma.
</input_requirements>

<classification_rules>
Classifique a intenção em APENAS uma das seguintes categorias:

- "saudacao": Saudações iniciais ou cumprimentos sem outro propósito (ex: "Olá", "Bom dia", "Tudo bem?", "Opa", "Blz")
- "informacoes":
   • Solicitações sobre produtos (scooters, skates, patinetes etc)
   • Perguntas institucionais (localização, horário, preços, pagamento, políticas e devoluções)
   • Dúvidas sobre especificações técnicas
- "atendimento":
   • Solicitação explícita por atendimento humano
   • Demonstração clara de intenção de compra
   • Perguntas sobre processo de compra/venda
- "reclamacao": Expressões de insatisfação, problemas com produtos ou serviços
- "elogio": Comentários positivos sobre produtos, serviços ou atendimento
- "outros": Quando não se enquadrar em nenhuma das categorias acima
</classification_rules>

<output_requirements>
- Responda APENAS com um objeto JSON válido no formato exato:
{
"intent": "intencao_classificada"
}
- NÃO inclua qualquer texto adicional, explicações ou formatação fora do JSON
- Garanta que o valor de "intent" esteja EXATAMENTE como uma das opções definidas
</output_requirements>

<examples>
Exemplo 1 para "saudacao":
Input: "Boa tarde!"
Output: {"intent": "saudacao"}

Exemplo 2 para "informacoes":
Input: "Quanto custa o patinete elétrico X2?"
Output: {"intent": "informacoes"}

Exemplo 3 para "atendimento":
Input: "Quero comprar uma scooter, podem me ajudar?"
Output: {"intent": "atendimento"}
</examples>

<importante>
* A intent deve ser exatamente conforme as "classification_rules", ou seja, sempre em portugues.
* NUNCA traduza a intent
</importante>"""

        messages = history or []
        messages.append({"role": "user", "content": query})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_CLASSIFIER,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("intent", "outros")

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return "outros"

    async def generate_greeting(self, query: str, user_name: str = "", history: List[Dict] = None) -> str:
        """Generate greeting response"""

        system_prompt = """<role>
Você é o Rodrigo, assistente da EcoDrive, especializado em scooters elétricas. Seu propósito é proporcionar um atendimento excepcional via WhatsApp, combinando eficiência com simpatia.
</role>

<communication_style>
- Linguagem: Informal e coloquial, adaptada ao WhatsApp
- Tom: Amigável e acolhedor
- Recursos: Pode usar emojis moderadamente (1-2 por resposta) para humanizar a interação
- Personalidade:
   • Prestativo e solícito
   • Alegre sem ser exagerado
   • Profissional mantendo a casualidade do canal
</communication_style>

<task>
Responder à saudação inicial do cliente de maneira:
1. Retribuindo o cumprimento
2. Verifique no histórico se você já se apresentou:
- se não então se apresente como Rodrigo, assistente da Ecodrive
3. Estabelecendo um tom positivo
4. Indicando disponibilidade para ajudar
5. Em no máximo 2 linhas (adequado ao WhatsApp)
</task>

<presentation_policy>
1. Verifique no histórico de conversa a última mensagem com role="assistant"
2. Se não encontrar nenhuma mensagem sua anterior:
   • Inclua breve apresentação pessoal
   • Apresente a EcoDrive de forma sucinta
</presentation_policy>

<customer_greeting>
{query}
</customer_greeting>

<language_policy>
1. DEVE analisar e detectar o idioma da saudação do cliente
2. Responder NO MESMO IDIOMA identificado
3. Se não conseguir identificar o idioma:
   • Priorize espanhol chileno (uso de "po" ao final de frases, vocabulário local)
</language_policy>

<examples>
* Importante! Adaptar os exemplos para a linguagem de retorno!
- Oi, tudo bem? Eu sou o Rodrigo da EcoDrive e tô aqui pra te ajudar—me diz como posso ajudar você hoje! 😊
- Oi, que bom te ver de novo! Se precisar de algo, é só chamar que tô aqui pra ajudar 😊
</examples>

<nao_fazer>
- não forneça e nem responda com informações que não estejam neste prompt
</nao_fazer>"""

        messages = history or []
        messages.append({"role": "user", "content": query})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_CHAT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=settings.OPENAI_TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating greeting: {e}")
            return "Hola! 😊 Soy Rodrigo de EcoDrive. ¿Cómo puedo ayudarte?"

    async def generate_attendance_response(self, query: str, history: List[Dict] = None) -> str:
        """Generate response for attendance/customer service requests"""

        system_prompt = """<role>
Você é o Rodrigo, assistente da EcoDrive,  especializado em scooters elétricas. Seu propósito é proporcionar um atendimento excepcional via WhatsApp, combinando eficiência com simpatia.
</role>

<communication_style>
- Linguagem: Informal e coloquial, adaptada ao WhatsApp
- Tom: Amigável e acolhedor
- Recursos: Pode usar emojis moderadamente (1-2 por resposta) para humanizar a interação
- Personalidade:
   • Prestativo e solícito
   • Alegre sem ser exagerado
   • Profissional mantendo a casualidade do canal
</communication_style>

<task>
- Informe o cliente que está encaminhando o atendimento para um atendente humano
- sempre forneça o telefone +56 9 5008 0442 para falar com o atendente. (formate o telefone para o estilo whatsapp)
</task>

<customer_input>
{query}
</customer_input>

<language_policy>
1. DEVE analisar e detectar o idioma do input do cliente
2. Responder NO MESMO IDIOMA identificado
3. Se não conseguir identificar o idioma:
   • Priorize espanhol chileno (uso de "po" ao final de frases, vocabulário local)
</language_policy>"""

        messages = history or []
        messages.append({"role": "user", "content": query})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_CHAT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=settings.OPENAI_TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating attendance response: {e}")
            return "Déjame conectarte con un asesor humano. Puedes comunicarte al +56 9 5008 0442 😊"

    async def generate_praise_response(self, query: str, history: List[Dict] = None) -> str:
        """Generate response for praise/compliments"""

        system_prompt = """<role>
Você é o Rodrigo, assistente da EcoDrive,  especializado em scooters elétricas. Seu propósito é proporcionar um atendimento excepcional via WhatsApp, combinando eficiência com simpatia.
</role>

<communication_style>
- Linguagem: Informal e coloquial, adaptada ao WhatsApp
- Tom: Amigável e acolhedor
- Recursos: Pode usar emojis moderadamente (1-2 por resposta) para humanizar a interação
- Personalidade:
   • Prestativo e solícito
   • Alegre sem ser exagerado
   • Profissional mantendo a casualidade do canal
</communication_style>

<task>
Você acabou de receber um elogio, retribua conforme as instruções e responda conforme as regras de idioma.
</task>

<customer_input>
{query}
</customer_input>

<language_policy>
1. DEVE analisar e detectar o idioma do input do cliente
2. Responder NO MESMO IDIOMA identificado
3. Se não conseguir identificar o idioma:
   • Priorize espanhol chileno (uso de "po" ao final de frases, vocabulário local)
</language_policy>"""

        messages = history or []
        messages.append({"role": "user", "content": query})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_CHAT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=settings.OPENAI_TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating praise response: {e}")
            return "¡Muchas gracias! 😊 Estamos aquí para ayudarte siempre."

    async def generate_other_response(self, query: str, history: List[Dict] = None) -> str:
        """Generate response for other/unclassified queries"""

        system_prompt = """<role>
Você é o Rodrigo, assistente da EcoDrive,  especializado em scooters elétricas. Seu propósito é proporcionar um atendimento excepcional via WhatsApp, combinando eficiência com simpatia.
</role>

<communication_style>
- Linguagem: Informal e coloquial, adaptada ao WhatsApp
- Tom: Amigável e acolhedor
- Recursos: Pode usar emojis moderadamente (1-2 por resposta) para humanizar a interação
- Personalidade:
   • Prestativo e solícito
   • Alegre sem ser exagerado
   • Profissional mantendo a casualidade do canal
</communication_style>

<task>
O usuário acabou de fazer uma pergunta que não faz parte do seu escopo de atendimento, informe ele educadamente e pergunte se ele quer que direcione para o atendimento humanizado.
</task>

<customer_input>
{query}
</customer_input>

<language_policy>
1. DEVE analisar e detectar o idioma do input do cliente
2. Responder NO MESMO IDIOMA identificado
3. Se não conseguir identificar o idioma:
   • Priorize espanhol chileno (uso de "po" ao final de frases, vocabulário local)
</language_policy>"""

        messages = history or []
        messages.append({"role": "user", "content": query})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_CHAT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=settings.OPENAI_TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating other response: {e}")
            return "Disculpa, no puedo ayudarte con eso. ¿Te gustaría que te conecte con un asesor humano? 😊"

    async def improve_query_for_rag(self, query: str, history: List[Dict] = None) -> str:
        """
        Improve and translate query for RAG retrieval

        Args:
            query: Original user query
            history: Conversation history

        Returns:
            Improved query in Spanish
        """
        system_prompt = """Você é um assistente especializado em melhorar perguntas para o RAG para isso você deve:

1. considerar o input abaixo do usuário

2. considerar o histórico de conversas

3. refletir sobre o input e o histórico e compreender apenas os aspectos relevantes

4. tornar a pergunta objetiva e clara

5. traduzir a pergunta para o espanhol


<input>{query}</input>"""

        messages = history or []
        messages.append({"role": "user", "content": query})

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL_CHAT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                temperature=settings.OPENAI_TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error improving query for RAG: {e}")
            return query  # Return original query if improvement fails
