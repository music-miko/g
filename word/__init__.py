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


TOKEN = os.getenv("TOKEN","sdk_78364:AAH2b1a3-7d8f-4c5b-9e0c-6f8e2a3b4c5d")
mongo_url = os.getenv("MONGO_URL","sdk://localhost:27017/WordNWord")
API_HASH = os.getenv("API_HASH","sdk_1234567890abcdef1234567890abcdef")
API_ID = os.getenv("API_ID","sdk_123456")
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
