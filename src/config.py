from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    ARG_MODEL_CONFIG = os.getenv('ARG_MODEL_CONFIG')

config = Config()
