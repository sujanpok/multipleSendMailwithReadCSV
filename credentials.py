import os
from cryptography.fernet import Fernet

# Function to generate a key for encryption/decryption
def generate_key():
    return Fernet.generate_key()

# Load or generate a key (usually store this securely)
key = None
if os.path.exists("secret.key"):
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
else:
    key = generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Initialize Fernet encryption/decryption
cipher_suite = Fernet(key)

def encrypt_password(password: str) -> str:
    # Encrypt the given password
    encrypted_password = cipher_suite.encrypt(password.encode())
    return encrypted_password.decode()

def decrypt_password(encrypted_password: str) -> str:
    # Decrypt the given password
    decrypted_password = cipher_suite.decrypt(encrypted_password.encode())
    return decrypted_password.decode()

def load_sender_credentials():
    # Load sender credentials from a file if they exist
    sender_email = None
    sender_password = None
    if os.path.exists("sender_credentials.txt"):
        with open("sender_credentials.txt", "r") as file:
            sender_email = file.readline().strip()  # Email remains in plaintext
            encrypted_password = file.readline().strip()  # Encrypted password
            sender_password = decrypt_password(encrypted_password)
    return sender_email, sender_password

def save_sender_credentials(sender_email, sender_password):
    # Save sender email (plaintext) and encrypted password to a file
    encrypted_password = encrypt_password(sender_password)
    with open("sender_credentials.txt", "w") as file:
        file.write(f"{sender_email}\n{encrypted_password}")
