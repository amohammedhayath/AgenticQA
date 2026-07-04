import os
from google import genai
from dotenv import load_dotenv
from google.genai import errors
from google.genai.types import HttpOptions

load_dotenv()

p_id = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
loc = os.getenv("GOOGLE_CLOUD_LOCATION")
os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = "True"

class LLM:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=p_id,  # Your exact credit-loaded project ID
            location=loc,
            http_options=HttpOptions(api_version="v1")
        )
    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                # model="gemini-3.1-pro-preview",
                contents=prompt
            )
            text = response.text or ""
            return text.strip()
        except errors.ClientError as e:
            print(f"[429] Capacity limit encountered. Backing off dynamically...")
            raise e