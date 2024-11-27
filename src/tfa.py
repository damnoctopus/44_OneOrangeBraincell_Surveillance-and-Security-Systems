import pyotp
import qrcode
import os
import json


# Directory to store secrets and QR codes
DATA_DIR = os.path.join(os.getcwd(), "fileData")
SECRETS_FILE = os.path.join(DATA_DIR, "secrets.json")


def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_secrets():
    """Load secrets from a file."""
    ensure_data_directory()
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_secrets(secrets):
    """Save secrets to a file."""
    ensure_data_directory()
    with open(SECRETS_FILE, "w") as f:
        json.dump(secrets, f)


def generate_2fa_secret(user_identifier):
    """Generate a new secret for the user."""
    secrets = load_secrets()

    if user_identifier in secrets:
        print(f"Secret for {user_identifier} already exists.")
        return secrets[user_identifier]

    secret = pyotp.random_base32()
    secrets[user_identifier] = secret
    save_secrets(secrets)

    print(f"New secret generated for {user_identifier}: {secret}")
    return secret


def generate_qr_code(secret, user_identifier, issuer_name="MyPasswordManager"):
    """Generate a QR code for the user."""
    # Generate the provisioning URI
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_identifier,
        issuer_name=issuer_name
    )

    # Determine the file path
    ensure_data_directory()
    qr_file = os.path.join(DATA_DIR, f"{user_identifier}_2fa_qr.png")

    # Check if the file already exists
    if os.path.exists(qr_file):
        print(f"QR Code for {user_identifier} already exists at {qr_file}.")
        return qr_file

    # Generate and save the QR code
    qr = qrcode.make(uri)
    qr.save(qr_file)
    print(f"QR Code generated and saved as {qr_file}")
    print("\nScan the QR Code using an authenticator app (e.g., Google Authenticator).")
    return qr_file


def validate_otp(secret, user_provided_otp):
    """Validate the OTP provided by the user."""
    totp = pyotp.TOTP(secret)
    return totp.verify(user_provided_otp)


import os

def two_factor_auth():
    print("Two-Factor Authentication")
    user_email = input("Enter your email to authenticate 2FA: ")

    # Check if the file exists and read content
    if os.path.exists('fileData/user.txt'):
        with open('fileData/user.txt', 'r') as file:
            file_content = file.read()

        if user_email != file_content:
            return False
    else:
        os.makedirs('fileData', exist_ok=True)
        # Store the user_email in the file
        with open('fileData/user.txt', 'w') as file:
            file.write(user_email)

    # Step 1: Retrieve or Generate Secret and QR Code
    secret = generate_2fa_secret(user_email)
    qr_file = generate_qr_code(secret, user_email)

    # Step 2: OTP Validation
    for i in range(3):
        user_otp = input("Enter the OTP from your authenticator app: ")

        if validate_otp(secret, user_otp):
            print("OTP Verified! Two-Factor has been Authenticated.")
            return True
        else:
            print("Invalid OTP. Please try again.")
    else:
        print("Failed to validate OTP after 3 attempts.")
        return False

