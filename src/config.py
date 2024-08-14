from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    JARVIS_MODEL_CONFIG = os.getenv('JARVIS_MODEL_CONFIG')

config = Config()
