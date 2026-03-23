from cryptography.fernet import Fernet
import base64
import hashlib


def generate_key(password: str) -> bytes:
    """
    Generates a secure Fernet key from a user-provided password
    using SHA-256 hashing.
    """
    hash_digest = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(hash_digest[:32])


def encrypt_data(data: bytes, password: str) -> bytes:
    """
    Encrypts evidence data using a password-based key.
    """
    key = generate_key(password)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)
    return encrypted_data


def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """
    Decrypts encrypted evidence data using the same password.
    """
    key = generate_key(password)
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data


def encrypt_file(file_path: str, password: str) -> bytes:
    """
    Reads a file and returns encrypted file content.
    """
    with open(file_path, "rb") as file:
        file_data = file.read()
    return encrypt_data(file_data, password)


def decrypt_file(encrypted_data: bytes, output_path: str, password: str):
    """
    Decrypts encrypted data and saves it to a file.
    """
    decrypted_data = decrypt_data(encrypted_data, password)
    with open(output_path, "wb") as file:
        file.write(decrypted_data)
