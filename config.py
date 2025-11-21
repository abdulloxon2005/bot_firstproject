import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL= os.getenv("API_URL")
PROFILE_URL=os.getenv("PROFILE_URL")