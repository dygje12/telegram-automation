import base64
import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class EncryptionManager:
    def __init__(self):
        # Get encryption key from environment or generate one
        key = os.getenv("ENCRYPTION_KEY")
        if not key or key == "your-32-byte-encryption-key-here-change-this":
            # Generate a new key if not set
            key = Fernet.generate_key().decode()
            print(f"Generated new encryption key: {key}")
            print("Please add this to your .env file as ENCRYPTION_KEY")

        if isinstance(key, str):
            key = key.encode()

        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        if not data:
            return ""

        encrypted_data = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data"""
        if not encrypted_data:
            return ""

        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")


# Global instance
encryption_manager = EncryptionManager()
