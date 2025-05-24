import os
from pyrogram import Client
import logging  
from motor.motor_asyncio import AsyncIOMotorClient
from pyromod import listen
from word.modules.word import load_words, load_common_words

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


TOKEN = os.getenv("TOKEN","8092284117:AAHjqmv2-RtmZEmyBWDoMDkEEEhX_AORKEM")
mongo_url = os.getenv("MONGO_URL","mongodb+srv://rohit6205881743:rohit6205881743@cluster0.soqtewz.mongodb.net/")
API_HASH = os.getenv("API_HASH","750432c8e1b221f91fd2c93a92710093")
API_ID = os.getenv("API_ID","28122413")


word = Client(
    "lol",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    plugins=dict(root="word"),
)

DEV_LIST = [7969722879]

client = AsyncIOMotorClient(mongo_url)
db = client['WordNWord']
user_Collection = db['user']
collection = db['word']

WORD_LIST = set(load_words())
WORD_SET = set(WORD_LIST)
MEAN_WORD = load_common_words()
MEAN_WORD_SET = set(MEAN_WORD)

print(f"Loaded {len(WORD_SET)} words from the word list.")
