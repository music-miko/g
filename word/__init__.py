import os
from pyrogram import Client
import logging  
from motor.motor_asyncio import AsyncIOMotorClient
import pyromod
from word.modules.word import load_words, load_common_words, load_state_city_countries


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


TOKEN = os.getenv("TOKEN","8450714119:AAG3qQ8JeNJfo0y9OsEp0MCX4CV00K1oqas")
mongo_url = os.getenv("MONGO_URL","mongodb+srv://word:Zp1oCmbxaJUnFNRH@deadline.g7gbxvy.mongodb.net/?retryWrites=true&w=majority&appName=deadline")
API_HASH = os.getenv("API_HASH","9a098f01aa56c836f2e34aee4b7ef963")
API_ID = os.getenv("API_ID","24620300")
if not TOKEN or not mongo_url or not API_HASH or not API_ID:
    raise ValueError("Please set the environment variables: TOKEN, MONGO_URL, API_HASH, and API_ID.")


word = Client(
    "lol",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    plugins=dict(root="word"),
)


DEV_LIST = [7321657753]

client = AsyncIOMotorClient(mongo_url)
db = client['WordNWord']
user_Collection = db['user']
collection = db['word']

WORD_LIST = set(load_words())
WORD_SET = set(WORD_LIST)
MEAN_WORD = load_common_words()
MEAN_WORD_SET = set(MEAN_WORD)
STATE_CITY_COUNTRY = load_state_city_countries()
COUNTRY_SET = set(STATE_CITY_COUNTRY["countries"])
STATE_SET = set(STATE_CITY_COUNTRY["states"])
CITY_SET = set(STATE_CITY_COUNTRY["cities"])
ALL_COUNTRY_SET = COUNTRY_SET | STATE_SET | CITY_SET
print(f"Loaded {len(COUNTRY_SET)} countries, {len(STATE_SET)} states, and {len(CITY_SET)} cities, and total {len(ALL_COUNTRY_SET)}.")
print(f"Loaded {len(WORD_SET)} words from the word list.")
