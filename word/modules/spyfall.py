from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
from pyrogram import filters
from word import word as spy
import asyncio
from word import DEV_LIST

spy_games = {}
temp_message_ids = {}

class SpyGame:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.players = []
        self.imposter = None
        self.common_word = ""
        self.imposter_word = ""
        self.explanations = {}
        self.votes = {}
        self.phase = "waiting"
        self.countdown_task = None
        self.starter = None
        self.current_player_index = 0
        self.explanation_message = None

    async def start_countdown(self):
        countdown = 60
        self.phase = "joining"
        while countdown > 0:
            await spy.send_message(self.chat_id, f"⏳ Game starting in {countdown} seconds! Use /joinspy to participate!")
            await asyncio.sleep(10)
            countdown -= 10
            if len(self.players) >= 6:
                break
        if 4 <= len(self.players) <= 6:
            await self.start_game()
        else:
            await spy.send_message(self.chat_id, "❌ Not enough players!")
            del spy_games[self.chat_id]

    async def start_game(self):
        words = [("Mountain", "Volcano"), ("River", "Lake"), ("Pizza", "Burger")]
        self.common_word, self.imposter_word = random.choice(words)
        self.imposter = random.choice(self.players)
        self.phase = "explain"
        for player in self.players:
            word = self.imposter_word if player == self.imposter else self.common_word
            try:
                await spy.send_message(player['id'], f"Your word: **{word}**")
            except:
                await spy.send_message(self.chat_id, f"❌ Failed to DM {player['mention']}")
        await self.prompt_next_explanation()

    async def prompt_next_explanation(self):
        if self.current_player_index >= len(self.players):
            await self.start_voting()
            return
        player = self.players[self.current_player_index]
        self.explanation_message = await spy.send_message(
            self.chat_id,
            f"{player['mention']} Explain your word! Reply to this message.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("View Word", url=f"t.me/ChainWordsBot")]])
        )

    async def handle_explanation(self, user_id, text):
        if user_id != self.players[self.current_player_index]['id']:
            return False
        self.explanations[user_id] = text
        self.current_player_index += 1
        await self.explanation_message.edit_text(f"Explanation received from {self.players[self.current_player_index-1]['mention']}!")
        await self.prompt_next_explanation()
        return True

    async def start_voting(self):
        self.phase = "voting"
        try:
            chat_link = await spy.export_chat_invite_link(self.chat_id)
        except Exception:
            try:
                chat = await spy.get_chat(self.chat_id)
                chat_link = chat.invite_link
            except Exception as e:
                print(f"Error getting chat link: {e}")
                chat_link = None
        for player in self.players:
            try:
                await spy.send_message(
                    player['id'],
                    "Vote for imposter:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(p['name'], callback_data=f"vote_{p['id']}_{self.chat_id}_{chat_link}")]
                        for p in self.players if p['id'] != player['id']
                    ])
                )
            except:
                pass    
        await spy.send_message(self.chat_id, "🗳️ Voting started! Check PMs!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Go To Votes", url=f"t.me/ChainWordsBot")]]))

    async def end_game(self):
        max_votes = max(self.votes.values(), default=0)
        candidates = [k for k,v in self.votes.items() if v == max_votes]
        eliminated = random.choice(candidates) if candidates else None
        is_imposter = eliminated == self.imposter['id'] if eliminated else False
        await spy.send_message(
            self.chat_id,
            f"🚨 {self.get_player(eliminated)['mention'] if eliminated else 'No one'} eliminated!"
            f"👤 Imposter: {self.imposter['mention']}"
            f"Common: {self.common_word} | Imposter: {self.imposter_word}"
            f"{'✅ Crew wins!' if is_imposter else '❌ Imposter wins!'}"
        )
        del spy_games[self.chat_id]

    async def force_start(self):
        if self.countdown_task:
            self.countdown_task.cancel()
        if 4 <= len(self.players) <= 6:
            await self.start_game()
        else:
            await spy.send_message(self.chat_id, "Need 4-6 players to start!")

    def get_player(self, user_id):
        return next((p for p in self.players if p['id'] == user_id), None)

    def get_player_have_explanation(self, user_id):
        return user_id in self.explanations

@spy.on_message(filters.command("startspy") & filters.group)
async def start_spy(client, message):
    chat_id = message.chat.id
    if chat_id in spy_games:
        return await message.reply("Game already running!")
    game = SpyGame(chat_id)
    spy_games[chat_id] = game
    game.starter = message.from_user.id
    game.countdown_task = asyncio.create_task(game.start_countdown())
    await message.reply("🕵️ Spy game starting in 60 seconds!\nUse /joinspy to join!")

@spy.on_message(filters.command("joinspy") & filters.group)
async def join_spy(client, message):
    game = spy_games.get(message.chat.id)
    if not game or game.phase != "joining":
        return
    try:
        await spy.send_message(
            message.from_user.id,
            "You joined the Spy game! Wait for the game to start."
        )
    except Exception:
        return await message.reply(
            "❌ Please start the bot in private and unblock it to join the game: [Start Bot](https://t.me/ChainWordsBot)",
            disable_web_page_preview=True
        )

    if any(p['id'] == message.from_user.id for p in game.players):
        return await message.reply("Already joined!")

    if len(game.players) >= 6:
        return await message.reply("Game is full! Cannot join.")

    game.players.append({
        'id': message.from_user.id,
        'mention': message.from_user.mention,
        'name': message.from_user.first_name
    })
    await message.reply(f"✅ {message.from_user.mention} joined! ({len(game.players)}/6)")

@spy.on_message(filters.command("forcestartspy") & filters.group)
async def force_start(client, message):
    game = spy_games.get(message.chat.id)
    if not game or game.phase != "joining":
        return
    if message.from_user.id != game.starter and message.from_user.id not in DEV_LIST:
        return await message.reply("Only game starter can force start!")
    await game.force_start()

@spy.on_message(filters.text & filters.group)
async def handle_explanations(client, message):
    game = spy_games.get(message.chat.id)
    if not game or game.phase != "explain":
        return
    player_ids = [p['id'] for p in game.players]
    if message.from_user.id not in player_ids:
        return  
    current_player = game.players[game.current_player_index]
    if message.reply_to_message and message.reply_to_message.text:
        if (
            "Explain your word!" not in message.reply_to_message.text
            and message.from_user.id != current_player['id']
        ):
            km = await message.reply("⚠️ Wait for your turn!")
            await asyncio.sleep(3)
            await km.delete()
            await message.delete()
            return
        if "Explain your word!" not in message.reply_to_message.text:
            return await message.reply("❌ Reply to the explanation prompt!")
        if message.reply_to_message.id == game.explanation_message.id:
            explanation = message.text
            await game.handle_explanation(message.from_user.id, explanation)
            await message.delete()
            if not hasattr(game, "all_explanations"):
                game.all_explanations = []
            game.all_explanations.append(f"{current_player['mention']}: {explanation}")
            summary_text = "✅ Users Explanations:\n" + "\n".join(game.all_explanations)
            if not hasattr(game, "explanation_summary_msg") or game.explanation_summary_msg is None:
                game.explanation_summary_msg = await spy.send_message(
                    game.chat_id,
                    "⌛ Waiting for explanations...\n\n" + summary_text,
                    disable_web_page_preview=True
                )
            else:
                try:
                    await spy.edit_message_text(
                        chat_id=game.chat_id,
                        message_id=game.explanation_summary_msg.id,
                        text=summary_text,
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    print("Edit failed:", e)

@spy.on_callback_query(filters.regex(r'^vote_'))
async def handle_vote_callback(client, query):
    game = spy_games.get(int(query.data.split("_")[2]))
    chat_link = query.data.split("_")[3] if len(query.data.split("_")) > 3 else None
    if not game:  
        await query.answer("Game no longer exists!")
        return
    try:
        if game.phase != "voting":  
            await query.answer("Voting closed!")
            return
        voted_id = int(query.data.split("_")[1])
        voter_id = query.from_user.id
        if voter_id not in [p['id'] for p in game.players]:
            await query.answer("You're not in this game!")
            return
        if voted_id not in [p['id'] for p in game.players]:
            await query.answer("Invalid player!")
            return
        game.votes[voted_id] = game.votes.get(voted_id, 0) + 1
        await query.answer(f"Voted for {game.get_player(voted_id)['name']}!")
        await query.message.delete()
        await spy.send_message(
            query.from_user.id,
            f"✅ You voted for {game.get_player(voted_id)['mention']}!", 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", url=f"{chat_link}" if chat_link else "https://t.me/ChainWordsBot")]
            ])
        )
        await spy.send_message(
            game.chat_id,
            f"🗳️ {query.from_user.mention} voted for {game.get_player(voted_id)['mention']}!"
        )
        if sum(game.votes.values()) == len(game.players):
            await game.end_game()
    except Exception as e:
        print(f"Vote error: {e}")
        await query.answer("Error processing vote!")

@spy.on_message(filters.command("stopspy") & filters.group)
async def stop_spy_game(client, message):
    chat_id = message.chat.id
    if chat_id not in spy_games:
        return await message.reply("No game running in this group!")
    if message.from_user.id not in DEV_LIST and spy_games[chat_id].starter != message.from_user.id:
        return await message.reply("Only the game starter can stop the game!")
    del spy_games[chat_id]
    if temp_message_ids.get(chat_id):
        del temp_message_ids[chat_id]
    await message.reply("🛑 Spy game stopped!\nData Cleared")
