from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from word.database.db import add_user, get_user, add_group, get_group
from word import word

START_TEXT = """👋 **Hello {user}!**

🎮 Welcome to **{bot}** – your all-in-one word game bot for Telegram groups!

🕹️ **Games Available:**
• 🐊 Crocodile  
• 🗺️ Atlas  
• 🔗 Word Chain  
• 🕵️ Spyfall

➕ **Add me to a group** and send ```/startclassic``` to start playing!
"""

HELP_TEXT = """🆘 **How to Play and Commands Overview**

✏️ **Classic Word Chain Game**
• `/startclassic` - Start a new classic word chain game
• `/join` - Join a pending game
• `/flee` - Leave a pending game
• `/extend` - Extend start countdown by 30 seconds
• `/forcestart` - Force start the game (starter only)

🐊 **Crocodile Game Help**
• `/host` - Start hosting a word guessing game
• `/stopgame` - Stop current host game (host only)

🗺 **Atlas Game Help**
• Each player must say a valid city or country
• Word must start with the last letter of the previous word

🕵️ **Spyfall Game Help**
• One player is spy, others must guess who
• Spy tries to guess the location
"""

# ▶ START command
@word.on_message(filters.command(["start"]))
async def start(client: Client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    first_name = message.from_user.first_name

    if not await get_user(user_id):
        await add_user(user_id, user_name, first_name)

    if message.chat.type in ["group", "supergroup"]:
        if not await get_group(message.chat.id):
            await add_group(message.chat.id, message.chat.title)

    await message.reply_photo(
        photo="https://files.catbox.moe/pqntlh.jpg",
        caption=START_TEXT.format(
            user=message.from_user.mention,
            bot=(await client.get_me()).first_name
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📘 Help", callback_data="help_main")],
                [
                    InlineKeyboardButton("📡 Updates", url=f"https://t.me/DeadlineTechTeam"),
                    InlineKeyboardButton("🏪 Support", url=f"https://t.me/DeadlineTechSupport")
                ],
                [
                    InlineKeyboardButton("➕ Add me to Your Chat ➕", url=f"https://t.me/ChainWordsBot?startgroup=true")
                ]
            ]
        )
    )

# ▶ HELP command
@word.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(HELP_TEXT)

# ▶ CALLBACK handlers
@word.on_callback_query(filters.regex("help_main"))
async def help_main(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        HELP_TEXT,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✏️ Word Chain Game", callback_data="help_classic"),
                InlineKeyboardButton("🐊 Crocodile Game", callback_data="help_host")
            ],
            [
                InlineKeyboardButton("🕵️ Spyfall Game", callback_data="help_other"),
                InlineKeyboardButton("🗺 Atlas Game", callback_data="help_general")
            ]
        ])
    )
    await callback_query.answer()

@word.on_callback_query(filters.regex("help_classic"))
async def help_classic(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        """✏️ **Classic Word Chain Game Help**

How to Start:
• `/startclassic` - Start a game
• `/join` - Join pending game
• `/forcestart` - Force start early
• `/extend` - Add 30 seconds to countdown
• `/flee` - Leave pending game

Game Rules:
• Each word must begin with the last letter of the previous word
• Starts with random letter
• 45s per turn, shortens as game goes
• Last standing player wins!
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Help", callback_data="help_main")]
        ])
    )
    await callback_query.answer()

@word.on_callback_query(filters.regex("help_host"))
async def help_host(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        """🐊 **Crocodile Game Help**

How to Start:
• `/host` - Start hosting a word guessing round
• Inline buttons show/hide word or skip word
• `/stopgame` - Stop the game

How to Play:
• Users guess the word by typing in chat
• First correct guess wins the round
• Host cannot guess
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Help", callback_data="help_main")]
        ])
    )
    await callback_query.answer()

@word.on_callback_query(filters.regex("help_other"))
async def help_other(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        """🗺 **Atlas Game Help**
        
🗺️ **Atlas**
• Each player must say a valid city or country
• Word must start with the last letter of the previous word

""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Help", callback_data="help_main")]
        ])
    )
    await callback_query.answer()

@word.on_callback_query(filters.regex("help_general"))
async def help_general(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        """🕵️ **Spyfall Game Help**

🕵️ **Spyfall**
• One player is spy, others must guess who
• Spy tries to guess the location
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Help", callback_data="help_main")]
        ])
    )
    await callback_query.answer()
