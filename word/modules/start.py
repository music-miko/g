from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
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

❓Need help? Ping @DeadlineTechSupport"""

@word.on_message(filters.command(["start", "help"]))
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
            )
        )
    else:
        await message.reply_photo(
            photo="https://files.catbox.moe/pqntlh.jpg",
            caption=START_TEXT.format(
                user=message.from_user.mention,
                bot=(await client.get_me()).first_name
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("➕ Add Me ➕", url="https://t.me/ChainWordsBot?startgroup=true"),
                    ]
                ]
            )
        )
