import google.generativeai as genai


def check_strenth(password):
    genai.configure(api_key="AIzaSyCO7y3n4NZHnRtdNnhjOYY7fmNS8VJtIQA")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"""
    Evaluate if the following password is strong or not. The password is evaluated based on length, variety of characters, and complexity:
    - At least 8 characters
    - Uppercase and lowercase letters
    - Numbers and special characters included
    - Avoids easily guessable patterns
    Password: {password}
    suggest stronger passwords that are similar to the given password
    Max limit of response:50words

    """)
    print(response.text)


# main
check_strenth("")