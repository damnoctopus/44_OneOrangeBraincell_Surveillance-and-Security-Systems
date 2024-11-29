from flask import Flask, request, jsonify, render_template, redirect, url_for
import pyotp
import qrcode
import passStoreFunc as fs
import tfa
import func as fc
import os
import shutil
import json

app = Flask(__name__)

# Ensure the encryption key exists
if not os.path.exists('fileData/secret.key'):
    fs.generate_key()


# Home page
@app.route('/')
def home():
    path="C:\\Users\\madha\\PycharmProjects\\44_OneOrangeBraincell_Surveillance-and-Security-Systems\\src\\templates\\home.html"
    return render_template("home.html")  # Renders the home page with 5 buttons


# Add Password
@app.route('/add', methods=['GET', 'POST'])
def add_password():
    if request.method == 'POST':
        from google.generativeai import configure, GenerativeModel

        # Configure the Google Generative AI model
        configure(api_key="AIzaSyCO7y3n4NZHnRtdNnhjOYY7fmNS8VJtIQA")
        model = GenerativeModel("gemini-1.5-flash")

        # Retrieve user input from the form
        website = request.form.get("website")
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            # Call the model to evaluate password strength
            response = model.generate_content(
                f"""
                Evaluate if the following password is strong or not. The password is evaluated based on:
                - At least 8 characters
                - Uppercase and lowercase letters
                - Numbers and symbols included
                - Avoids easily guessable patterns
                Password: {password}
                Return ONLY "true" if the password is strong, or "false" if the password is weak.
                Additionally, suggest stronger passwords if the password is weak. Limit response to 50 words.
                """
            )

            response_text = response.text.strip().lower()

            if "true" in response_text:
                # Password is strong, encrypt and save it
                encrypted_password = fs.encrypt_data(password)
                fs.save_password(website, username, encrypted_password)
                return jsonify({"message": f"Password for {website} has been added successfully."})
            elif "false" in response_text:
                # Password is weak, extract suggestions if available
                suggestions = response_text.split("false")[-1].strip()
                return jsonify({
                    "message": "Password is weak.",
                    "suggestions": suggestions
                })
            else:
                return jsonify({
                    "error": "Unexpected response from the AI model.",
                    "response": response_text
                })

        except Exception as e:
            return jsonify({"error": f"An error occurred: {e}"}), 500
    else:
        return render_template('add.html')  # Render the add password form page





# Retrieve Password
@app.route('/retrieve', methods=['GET', 'POST'])
def retrieve_password():
    if request.method == 'POST':
        website = request.form.get('website')

        # Perform 2FA before retrieving
        if tfa.two_factor_auth():
            passwords = fs.load_passwords()
            for entry in passwords:
                if entry[0] == website:
                    decrypted_password = fs.decrypt_data(entry[2].encode())
                    return jsonify({
                        "username": entry[1],
                        "password": decrypted_password
                    })
            return jsonify({"message": "No password found for the given website."})
        else:
            return jsonify({"message": "Failed to verify 2FA."})
    return render_template('retrieve.html')  # Render the retrieve password page





# Reset 2FA
@app.route('/reset_2fa', methods=['POST'])
def reset_2fa():
    response = request.form.get('response').lower()
    if response == 'y':
        shutil.rmtree('fileData')
        return jsonify({"message": "2FA has been reset."})
    elif response == 'n':
        return jsonify({"message": "Reset cancelled."})
    else:
        return jsonify({"message": "Invalid option."})


# Generate Strong Password
@app.route('/generate_password', methods=['GET'])
def generate_password():
    strong_password = fc.Genstrongpass()
    return jsonify({"strong_password": strong_password})


DATA_DIR = os.path.join(os.getcwd(), "fileData")
SECRETS_FILE = os.path.join(DATA_DIR, "secrets.json")

# Ensure the data directory exists
def ensure_data_directory():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created directory: {DATA_DIR}")

    # Ensure secrets file exists
    if not os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE, "w") as f:
            json.dump({}, f)  # Initialize an empty JSON object
        print(f"Created secrets file: {SECRETS_FILE}")


# Load secrets from the JSON file
def load_secrets():
    """Load secrets from a file."""
    ensure_data_directory()
    if os.path.exists(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Handle invalid JSON file
            print(f"Error: {SECRETS_FILE} contains invalid JSON. Resetting secrets.")
            return {}
        except Exception as e:
            # Handle any other unexpected error
            print(f"Unexpected error while loading secrets: {e}")
            return {}
    return {}


# Save secrets to the JSON file
def save_secrets(secrets):
    ensure_data_directory()
    with open(SECRETS_FILE, "w") as f:
        json.dump(secrets, f)

# Generate a new 2FA secret for the user
def generate_2fa_secret(user_identifier):
    secrets = load_secrets()

    if user_identifier in secrets:
        return None, "Secret for this user already exists."

    secret = pyotp.random_base32()
    secrets[user_identifier] = secret
    save_secrets(secrets)

    return secret, "New secret generated successfully."

# Generate a QR code for the secret
def generate_qr_code(secret, user_identifier, issuer_name="MyPasswordManager"):
    """Generate and save QR code for 2FA setup."""
    # Generate provisioning URI
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_identifier,
        issuer_name=issuer_name
    )

    # Define file path in static directory
    static_dir = os.path.join("static", "fileData")
    os.makedirs(static_dir, exist_ok=True)  # Ensure the directory exists
    qr_file_path = os.path.join(static_dir, f"{user_identifier}_2fa_qr.png")

    # Generate QR code and save
    qr = qrcode.make(uri)
    qr.save(qr_file_path)

    return qr_file_path

# Setup 2FA route
@app.route('/setup_2fa', methods=['GET', 'POST'])

def setup_2fa():
    if request.method == 'POST':
        # Step 1: Get the user's email from the form
        user_email = request.form.get('email')
        if not user_email:
            return render_template('setup_2fa.html', message="Email is required to set up 2FA.")

        # Step 2: Generate secret and QR code for the user
        secret = generate_2fa_secret(user_email)
        qr_file = generate_qr_code(secret, user_email)

        # Step 3: Pass QR code path and message to the front end
        qr_code_path = url_for('static', filename=f"fileData/{os.path.basename(qr_file)}")
        return render_template(
            'setup_2fa.html',
            message="Scan the QR code below with your authenticator app.",
            qr_code_path=qr_code_path
        )

    # Render page for GET requests
    return render_template('setup_2fa.html')


@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    user_email = request.form.get('email')
    if not user_email:
        return render_template('setup_2fa.html', message="Email is required to set up 2FA.")

    secret = generate_2fa_secret(user_email)
    qr_file_path = generate_qr_code(secret, user_email)

    # Generate the URL for the static file
    qr_code_url = url_for('static', filename=f"fileData/{os.path.basename(qr_file_path)}")
    return render_template(
        'verify_2fa.html',
        email=user_email,
        qr_code_path=qr_code_url
    )

def validate_otp(secret, otp):
    """Validate a given OTP against the user's TOTP secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)



@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    # Get the user's email and entered OTP
    user_email = request.form.get('email')
    user_otp = request.form.get('otp')
    if not user_email or not user_otp:
        return render_template('verify_2fa.html', message="Email and OTP are required.")

    # Load the secret for the user
    secrets = load_secrets()
    secret = secrets.get(user_email)
    if not secret:
        return render_template('setup_2fa.html', message="No 2FA setup found for this email.")

    # Validate the OTP
    if validate_otp(secret, user_otp):
        return render_template('success.html', message="2FA setup complete! Your OTP was verified.")
    else:
        return render_template('verify_2fa.html', email=user_email, message="Invalid OTP. Please try again.")




if __name__ == '__main__':
    app.run(debug=True)
