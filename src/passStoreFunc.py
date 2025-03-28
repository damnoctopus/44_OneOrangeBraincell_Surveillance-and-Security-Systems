import shutil
import os
from cryptography.fernet import Fernet


def generate_key():
    # Ensure the directory exists
    os.makedirs('fileData', exist_ok=True)

    # Generate and save the key
    key = Fernet.generate_key()
    with open('fileData/secret.key', 'wb') as key_file:
        key_file.write(key)


def load_key():
    # Ensure the key file exists
    if not os.path.exists('fileData/secret.key'):
        raise FileNotFoundError("Key file not found. Please generate a key first.")
    return open('fileData/secret.key', 'rb').read()


def encrypt_data(data):
    #function for encryption
    key = load_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return encrypted


def decrypt_data(encrypted_data):
    #function for decryption
    key = load_key()
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_data).decode()
    return decrypted


def save_password(website, username, encrypted_password):
    #save/append data to file
    with open('fileData/passwords.txt', 'a') as file:
        file.write(f"{website}|{username}|{encrypted_password.decode()}\n")


def load_passwords():
    #load data to ram
    if not os.path.exists('fileData/passwords.txt'):
        return []
    with open('fileData/passwords.txt', 'r') as file:
        return [line.strip().split('|') for line in file.readlines()]

def reset2fa():
    shutil.rmtree('fileData')