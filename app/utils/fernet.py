from cryptography.fernet import Fernet
from app.config import settings


_fernet = Fernet(settings.fernet_key)


def encrypt(data: str) -> bytes:
    encrypted_data = _fernet.encrypt(data.encode())
    return encrypted_data


def decrypt(encrypted_data: bytes) -> str:
    decrypted_data = _fernet.decrypt(encrypted_data)
    return decrypted_data.decode()
