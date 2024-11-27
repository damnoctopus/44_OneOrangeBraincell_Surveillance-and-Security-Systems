import pyotp
import qrcode

import os
import base64


# 1. Generate a Secret Key for a New User
def generate_2fa_secret(user_identifier):
    # Create a unique base32 secret
    secret = pyotp.random_base32()
    print(f"Secret for {user_identifier}: {secret}")

    # Save or associate this secret with the user's account in your database
    return secret


# 2. Generate a QR Code for Enrollment
def generate_qr_code(secret, user_identifier, issuer_name="MyPasswordManager"):
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_identifier,
        issuer_name=issuer_name
    )
    qr = qrcode.make(uri)
    qr_file =  os.path.join("D:\\Qr_codes", f"{user_identifier}_2fa_qr.png")
    qr.save(qr_file)
    print(f"QR Code generated and saved as {qr_file}")
    return qr_file




# 3. Validate OTP During Login
def validate_otp(secret, user_provided_otp):
    totp = pyotp.TOTP(secret)
    return totp.verify(user_provided_otp)





# Full Integration Example
if __name__ == "__main__":
    print("Two-Factor Authentication")
    user_email = input("Enter your email to set up 2FA: ")

    # Step 1: Generate Secret and QR Code
    secret = generate_2fa_secret(user_email)
    qr_file = generate_qr_code(secret, user_email)

    print("\nScan the QR Code using an authenticator app (e.g., Google Authenticator).")
    print("The QR Code has been saved to your device.")
    i = 0
    # Step 2: OTP Validation
    while (i < 3):
        print("\nNow, let's validate your OTP.")
        user_otp = input("Enter the OTP from your authenticator app: ")

        if validate_otp(secret, user_otp):
            print("OTP Verified! Two-Factor Authentication setup is successful.")
            break
        else:
            print("Invalid OTP. Please try again.")
        i = i+1
