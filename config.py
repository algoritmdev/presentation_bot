import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMINS = [int(x) for x in os.getenv("ADMINS", "").split(",") if x]
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

CARD_NUMBER = os.getenv("CARD_NUMBER", "8600 0000 0000 0000")

def update_card_number(new_card: str):
    global CARD_NUMBER
    CARD_NUMBER = new_card
