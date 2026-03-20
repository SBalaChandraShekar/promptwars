import os
from google import genai
from google.genai import errors
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

models_to_test = [
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.0-flash',
    'gemini-2.5-pro'
]

with open('test_results.txt', 'w') as f:
    for model_name in models_to_test:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hello, this is a test."
            )
            print(f"SUCCESS: {model_name}")
            f.write(f"SUCCESS: {model_name}\n")
        except errors.ClientError as e:
            print(f"ERROR for {model_name}: {e}")
            f.write(f"ERROR for {model_name}: {e}\n")
        except Exception as e:
            print(f"UNEXPECTED ERROR for {model_name}: {e}")
            f.write(f"UNEXPECTED ERROR for {model_name}: {e}\n")
