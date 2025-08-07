import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Tuple

from telethon import TelegramClient, events
from telethon.errors import (
    ChatAdminRequiredError,
    ChatWriteForbiddenError,
    FloodWaitError,
    PasswordHashInvalidError,
    PeerIdInvalidError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    SlowModeWaitError,
    UserBannedInChannelError,
)
from telethon.tl.types import Channel, Chat, User

from app.utils.encryption import encryption_manager

logger = logging.getLogger(__name__)


class TelegramService:
    def __init__(self):
        self.clients: Dict[str, TelegramClient] = {}
        self.temp_clients: Dict[str, TelegramClient] = {}  # For authentication process

    async def create_temp_client(self, api_id: str, api_hash: str, phone_number: str) -> str:
        """Create a temporary client for authentication"""
        try:
            # Create a temporary session file
            temp_session = tempfile.NamedTemporaryFile(delete=False, suffix=".session")
            session_path = temp_session.name
            temp_session.close()

            client = TelegramClient(session_path, int(api_id), api_hash)
            await client.connect()

            # Store temp client
            self.temp_clients[phone_number] = client

            return session_path
        except Exception as e:
            logger.error(f"Failed to create temp client: {str(e)}")
            raise Exception(f"Failed to create Telegram client: {str(e)}")

    async def send_code_request(self, api_id: str, api_hash: str, phone_number: str) -> bool:
        """Send authentication code to phone number"""
        try:
            session_path = await self.create_temp_client(api_id, api_hash, phone_number)
            client = self.temp_clients[phone_number]

            # Send code request
            await client.send_code_request(phone_number)
            return True

        except PhoneNumberInvalidError:
            raise Exception("Invalid phone number")
        except Exception as e:
            logger.error(f"Failed to send code: {str(e)}")
            raise Exception(f"Failed to send verification code: {str(e)}")

    async def verify_code(self, phone_number: str, code: str) -> Tuple[bool, bool]:
        """
        Verify the authentication code
        Returns: (success, needs_2fa)
        """
        try:
            if phone_number not in self.temp_clients:
                raise Exception("No active authentication session")

            client = self.temp_clients[phone_number]

            try:
                await client.sign_in(phone_number, code)
                return True, False
            except SessionPasswordNeededError:
                return True, True

        except PhoneCodeInvalidError:
            raise Exception("Invalid verification code")
        except Exception as e:
            logger.error(f"Failed to verify code: {str(e)}")
            raise Exception(f"Failed to verify code: {str(e)}")

    async def verify_2fa(self, phone_number: str, password: str) -> bool:
        """Verify 2FA password"""
        try:
            if phone_number not in self.temp_clients:
                raise Exception("No active authentication session")

            client = self.temp_clients[phone_number]

            await client.sign_in(password=password)
            return True

        except PasswordHashInvalidError:
            raise Exception("Invalid 2FA password")
        except Exception as e:
            logger.error(f"Failed to verify 2FA: {str(e)}")
            raise Exception(f"Failed to verify 2FA password: {str(e)}")

    async def finalize_auth(self, phone_number: str) -> str:
        """Finalize authentication and return encrypted session data"""
        try:
            if phone_number not in self.temp_clients:
                raise Exception("No active authentication session")

            client = self.temp_clients[phone_number]

            # Get session data
            session_data = client.session.save()

            # Encrypt session data
            encrypted_session = encryption_manager.encrypt(session_data.hex())

            # Clean up temp client
            await client.disconnect()
            del self.temp_clients[phone_number]

            return encrypted_session

        except Exception as e:
            logger.error(f"Failed to finalize auth: {str(e)}")
            raise Exception(f"Failed to finalize authentication: {str(e)}")

    async def create_client(
        self, user_id: int, api_id: str, api_hash: str, session_data: str
    ) -> bool:
        """Create and connect a client from saved session"""
        try:
            # Decrypt session data
            decrypted_session = encryption_manager.decrypt(session_data)
            session_bytes = bytes.fromhex(decrypted_session)

            # Create temporary session file
            temp_session = tempfile.NamedTemporaryFile(delete=False, suffix=".session")
            session_path = temp_session.name
            temp_session.close()

            # Create client
            client = TelegramClient(session_path, int(api_id), api_hash)

            # Load session
            client.session.load(session_bytes)

            # Connect
            await client.connect()

            # Verify connection
            if not await client.is_user_authorized():
                raise Exception("Session is no longer valid")

            # Store client
            self.clients[str(user_id)] = client

            return True

        except Exception as e:
            logger.error(f"Failed to create client: {str(e)}")
            raise Exception(f"Failed to create Telegram client: {str(e)}")

    async def get_client(self, user_id: int) -> Optional[TelegramClient]:
        """Get client for user"""
        return self.clients.get(str(user_id))

    async def disconnect_client(self, user_id: int):
        """Disconnect and remove client"""
        client_key = str(user_id)
        if client_key in self.clients:
            await self.clients[client_key].disconnect()
            del self.clients[client_key]

    async def resolve_group(
        self, client: TelegramClient, group_input: str
    ) -> Tuple[str, str, Optional[str]]:
        """
        Resolve group information from input
        Returns: (group_id, group_name, username)
        """
        try:
            entity = await client.get_entity(group_input)

            if isinstance(entity, (Channel, Chat)):
                group_id = str(entity.id)
                if hasattr(entity, "megagroup") and entity.megagroup:
                    group_id = f"-100{entity.id}"
                elif isinstance(entity, Channel):
                    group_id = f"-100{entity.id}"
                else:
                    group_id = f"-{entity.id}"

                group_name = entity.title
                username = getattr(entity, "username", None)

                return group_id, group_name, username
            else:
                raise Exception("Invalid group type")

        except Exception as e:
            logger.error(f"Failed to resolve group: {str(e)}")
            raise Exception(f"Failed to resolve group: {str(e)}")

    async def send_message(self, client: TelegramClient, group_id: str, message: str) -> bool:
        """Send message to group"""
        try:
            await client.send_message(int(group_id), message)
            return True

        except SlowModeWaitError as e:
            # Return the wait time for slow mode handling
            raise SlowModeWaitError(f"Slow mode active, wait {e.seconds} seconds")
        except FloodWaitError as e:
            # Return the wait time for flood handling
            raise FloodWaitError(f"Flood wait, wait {e.seconds} seconds")
        except (ChatWriteForbiddenError, UserBannedInChannelError, ChatAdminRequiredError):
            raise Exception("No permission to send messages to this group")
        except PeerIdInvalidError:
            raise Exception("Invalid group ID or group not accessible")
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            raise Exception(f"Failed to send message: {str(e)}")

    async def test_group_access(self, client: TelegramClient, group_id: str) -> bool:
        """Test if we can access and send messages to a group"""
        try:
            # Try to get group info
            entity = await client.get_entity(int(group_id))

            # Check if we can send messages (this is a basic check)
            # In a real scenario, you might want to check permissions more thoroughly
            return True

        except Exception as e:
            logger.error(f"Group access test failed: {str(e)}")
            return False

    async def get_me(self, client: TelegramClient) -> Dict:
        """Get current user information"""
        try:
            me = await client.get_me()
            return {
                "id": me.id,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "username": me.username,
                "phone": me.phone,
            }
        except Exception as e:
            logger.error(f"Failed to get user info: {str(e)}")
            raise Exception(f"Failed to get user information: {str(e)}")


# Global instance
telegram_service = TelegramService()
