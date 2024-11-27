import pyotp
import qrcode
import os
import tkinter as tk
import json
from tkinter import messagebox, simpledialog


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
        messagebox.showerror("Error", f"Secret for {user_identifier} already exists.")
        return secrets[user_identifier]

    secret = pyotp.random_base32()
    secrets[user_identifier] = secret
    save_secrets(secrets)

    messagebox.showinfo("Success", f"New secret generated for {user_identifier}: {secret}")
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
        messagebox.showinfo("Error", f"QR Code for {user_identifier} already exists at {qr_file}.")
        return qr_file

    # Generate and save the QR code
    qr = qrcode.make(uri)
    qr.save(qr_file)
    return qr_file


def validate_otp(secret, user_provided_otp):
    """Validate the OTP provided by the user."""
    totp = pyotp.TOTP(secret)
    return totp.verify(user_provided_otp)


def two_factor_auth():
    def verify_otp():
        user_name = user_entry.get()

        # Check if the file exists and read content
        if os.path.exists('fileData/user.txt'):
            with open('fileData/user.txt', 'r') as file:
                file_content = file.read()

            if user_name != file_content:
                messagebox.showerror("Auth Error", "Email does not match.")
                return False
        else:
            os.makedirs('fileData', exist_ok=True)
            # Store the user_email in the file
            with open('fileData/user.txt', 'w') as file:
                file.write(user_name)

        # Step 1: Retrieve or Generate Secret and QR Code
        secret = generate_2fa_secret(user_name)
        qr_file = generate_qr_code(secret, user_name)

        # Step 2: OTP Validation
        for i in range(3):
            user_otp = otp_entry.get()  # Get OTP from the entry field

            if validate_otp(secret, user_otp):
                messagebox.showinfo("Success", "OTP Verified! Two-Factor has been Authenticated.")
                return True
            else:
                messagebox.showwarning("Invalid OTP", "Invalid OTP. Please try again.")
        else:
            messagebox.showerror("Failed OTP", "Failed to validate OTP after 3 attempts.")
            return False

    # Tkinter window setup
    root = tk.Tk()
    retrieve_window = tk.Toplevel(root)
    retrieve_window.title("Two-Factor Authentication")

    tk.Label(retrieve_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
    user_entry = tk.Entry(retrieve_window)
    user_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(retrieve_window, text="Enter OTP:").grid(row=1, column=0, padx=10, pady=5)
    otp_entry = tk.Entry(retrieve_window)
    otp_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Button(retrieve_window, text="Verify", command=verify_otp).grid(row=2, column=0, columnspan=2, pady=10)



