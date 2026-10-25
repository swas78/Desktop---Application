# For: Authentication, password hashing, and local file encryption utilities
# Must never: Expose cryptographic private keys or allow token validation bypass

import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
import jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from engine.app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decodes and validates a JWT token; returns payload or None."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except (jwt.PyJWTError, ValueError):
        return None


def get_encryption_key() -> bytes:
    """Derives a 256-bit AES-GCM key from the local secret."""
    return hashlib.sha256(settings.jwt_secret.encode("utf-8")).digest()


def encrypt_bytes(data: bytes) -> bytes:
    """Encrypts bytes using AES-256-GCM with a random 12-byte nonce."""
    aesgcm = AESGCM(get_encryption_key())
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, data, None)
    return nonce + ciphertext


def decrypt_bytes(encrypted_data: bytes) -> bytes:
    """Decrypts AES-256-GCM bytes using the embedded 12-byte nonce."""
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    aesgcm = AESGCM(get_encryption_key())
    return aesgcm.decrypt(nonce, ciphertext, None)


def compute_sha256(data: bytes) -> str:
    """Computes hexadecimal SHA-256 digest of input bytes."""
    return hashlib.sha256(data).hexdigest()
