from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from word.database.db import add_user, get_user, add_group, get_group
from word import word
import collection, user_Collection

START_TEXT = """👋 **Hello {user}!**

🎮 Welcome to **{bot}** – your all-in-one word game bot for Telegram groups!

🕹️ **Games Available:**
• 🐊 Crocodile  
• 🌎 Atlas  
• ✏️ Word Chain  
• 🕵️ Spyfall

➕ **Add me to a group** and send `/startclassic` to start playing!
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
                    InlineKeyboardButton("📡 Updates", url="https://t.me/DeadlineTechTeam"),
                    InlineKeyboardButton("🏪 Support", url="https://t.me/DeadlineTechSupport")
                ],
                [InlineKeyboardButton("➕ Add me to Your Chat ➕", url="https://t.me/ChainWordsBot?startgroup=true")]
            ]
        )
    )

# ▶ HELP command (Updated)
@word.on_message(filters.command("help"))
async def help_cmd(client: Client, message: Message):
    await message.reply_text(
        "**🆘 Select a game below to view how to play:**",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✏️ Word Chain Game", callback_data="help_classic"),
                InlineKeyboardButton("🐊 Crocodile Game", callback_data="help_host")
            ],
            [
                InlineKeyboardButton("🕵️ Spyfall Game", callback_data="help_other"),
                InlineKeyboardButton("🌎 Atlas Game", callback_data="help_general")
            ]
        ])
    )

@word.on_message(filters.command("stats") & filters.user(7321657753))
async def dev_stats(client, message: Message):
    user_docs = await collection.find({}).to_list(length=None)
    group_docs = await user_Collection.find({}).to_list(length=None)

    total_users = sum(1 for doc in user_docs if doc.get("id", 0) > 0)
    total_groups = sum(1 for doc in group_docs if doc.get("id", 0) < 0)

    await message.reply(
        f"📊 **Developer Stats Panel**\n\n"
        f"👤 Registered Users: `{total_users}`\n"
        f"🏟️ Registered Groups: `{total_groups}`"
    )

# ▶ CALLBACK handlers
@word.on_callback_query(filters.regex("help_main"))
async def help_main(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "**🆘 Select a game below to view how to play:**",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✏️ Word Chain Game", callback_data="help_classic"),
                InlineKeyboardButton("🐊 Crocodile Game", callback_data="help_host")
            ],
            [
                InlineKeyboardButton("🕵️ Spyfall Game", callback_data="help_other"),
                InlineKeyboardButton("🌎 Atlas Game", callback_data="help_general")
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
• `/stats` - Get Your Word chain Statistics

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

@word.on_callback_query(filters.regex("help_general"))
async def help_general(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        """🌎 **Atlas Game Help**

`/startatlas` – Start a new Atlas game in the group
`/joinatlas` – Join a pending game
`/fleeatlas` – Leave the current game
`/extendatlas` – Extend the start countdown by 30s
`/forceatlas` – Force start the game (starter only)
`/atlasstats` – View your personal stats

🎯 **Game Rules:**
• First place starts with a random letter
• Each new place must start with the **last letter** of the previous place
• Minimum length starts at 3 letters
• Each player has **45 seconds** per turn
• Every 2 places → +1 minimum length
• Every 4 places → -10s time per turn (min 15s)
• No repetition of places!

🏆 **Victory:**
Last remaining player wins!
⛔ Invalid entries or timeouts = elimination

🎒 Tip: All city/state/country names are valid. Stay sharp!
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Help", callback_data="help_main")]
        ])
    )
    await callback_query.answer()

@word.on_callback_query(filters.regex("help_other"))
async def help_other(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        """🕵️ **Spyfall Game Help**

`/startspy` – Start a new game (group only)
`/joinspy` – Join an active game
`/forcestartspy` – Force start the game early
`/stopspy` – Cancel the game

🎮 **How to Play:**
• Players get secret words in PM
• 1 Imposter gets a different/fake word
• Take turns describing your word vaguely
• After all turns, vote privately for the imposter
• If imposter is caught = Crew wins, else Imposter wins!

👥 **Players: 4-6 required**
❗ Start the bot in PM before joining
💬 Ping us: @DeadlineTechSupport
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Help", callback_data="help_main")]
        ])
    )
    await callback_query.answer()
