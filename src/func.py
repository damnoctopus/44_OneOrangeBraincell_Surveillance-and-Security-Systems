import google.generativeai as genai


def check_strength(password):
    # Configure API
    genai.configure(api_key="AIzaSyCO7y3n4NZHnRtdNnhjOYY7fmNS8VJtIQA")
    model = genai.GenerativeModel("gemini-1.5-flash")

    try:
        # API call with timeout
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

        # Process the response
        response_text = response.text.strip().lower()

        if "true" in response_text:
            print("Password is strong!")
        elif "false" in response_text:
            print("Password is weak.")
            # Extract suggestions if available
            suggestions = response_text.split("false")[-1].strip()
            if suggestions:
                print("Suggestions:", suggestions)
        else:
            print("Unexpected response from the model:", response_text)

    except Exception as e:
        print(f"An error occurred: {e}")


# Main
check_strength("weakpass")  # Weak password example
check_strength("Clown@382$%")  # Strong password example
