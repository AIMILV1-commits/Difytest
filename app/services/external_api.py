"""
Service for external API calls
"""
import httpx
import logging
from typing import Optional, Dict, Any
from app.config import settings
from app.models.schemas import UserData

logger = logging.getLogger(__name__)


class ExternalAPIService:
    """Service for making external API calls"""

    def __init__(self):
        self.base_url = settings.RAG_API_BASE_URL
        self.api_key = settings.RAG_API_KEY
        self.timeout = httpx.Timeout(
            connect=settings.HTTP_CONNECT_TIMEOUT,
            read=settings.HTTP_READ_TIMEOUT
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_user_by_phone(self, phone: str) -> UserData:
        """
        Fetch user data by phone number

        Args:
            phone: User's phone number

        Returns:
            UserData object
        """
        url = f"{self.base_url}/api/v1/client/user-client/by-phone/{phone}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                data = response.json()

                return UserData(
                    id=data.get("id", 0) if isinstance(data.get("id"), int) else 0,
                    phone=str(data.get("phone", "")),
                    name=str(data.get("name", "")),
                    empresa=str(data.get("empresa", "")),
                    cb_intent=str(data.get("cb_intent", ""))
                )

        except httpx.HTTPError as e:
            logger.error(f"Error fetching user by phone {phone}: {e}")
            return UserData()  # Return default empty user data
        except Exception as e:
            logger.error(f"Unexpected error fetching user by phone {phone}: {e}")
            return UserData()

    async def notify_chatwoot_label(self, conversation_id: str) -> bool:
        """
        Notify Chatwoot with label for conversation

        Args:
            conversation_id: Dify conversation ID

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/api/v1/client/user-client/by-dify-conversation-id/{conversation_id}/chatwoot-label"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                logger.info(f"Successfully notified Chatwoot for conversation {conversation_id}")
                return True

        except httpx.HTTPError as e:
            logger.error(f"Error notifying Chatwoot for conversation {conversation_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error notifying Chatwoot: {e}")
            return False
