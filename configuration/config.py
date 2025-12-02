import os
from dotenv import load_dotenv

# Ensure we load .env from the project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DOTENV_PATH = os.path.join(ROOT, '.env')
load_dotenv(DOTENV_PATH)

TOKEN = os.getenv("DISCORD_TOKEN")
CR_USER_ID = int(os.getenv("CR_USER_ID", "0"))
CR_ROLE_NAME = os.getenv("CR_ROLE_NAME", "Class Representative")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CHANNEL_ID = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID", "0"))
