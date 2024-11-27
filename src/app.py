from flask import Flask, request, jsonify, render_template, redirect, url_for

import passStoreFunc as fs
import tfa
import func as fc
import os
import shutil

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
    @app.route('/add_password', methods=['POST'])
    def add_password():
        from google.generativeai import configure, GenerativeModel

        # Configure the Google Generative AI model
        configure(api_key="AIzaSyCO7y3n4NZHnRtdNnhjOYY7fmNS8VJtIQA")
        model = GenerativeModel("gemini-1.5-flash")

        # Retrieve user input from the form
        data = request.json
        website = data.get("website")
        username = data.get("username")
        password = data.get("password")

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


# Setup 2FA
@app.route('/setup_2fa', methods=['POST'])
def setup_2fa():
    if tfa.two_factor_auth():
        return jsonify({"message": "Two-Factor Authentication setup successful."})
    return jsonify({"message": "Failed to setup 2FA."})


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


if __name__ == '__main__':
    app.run(debug=True)
