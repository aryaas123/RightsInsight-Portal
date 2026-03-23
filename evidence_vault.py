from crypto_utils import encrypt_data, decrypt_data


def save_evidence(file, password):
    """
    Encrypts evidence file and returns encrypted bytes
    """
    file_bytes = file.read()
    encrypted_bytes = encrypt_data(file_bytes, password)
    return encrypted_bytes


def retrieve_evidence(encrypted_bytes, password):
    """
    Decrypts evidence file
    """
    decrypted_bytes = decrypt_data(encrypted_bytes, password)
    return decrypted_bytes
