import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from word import word
from word import ALL_COUNTRY_SET
from word.database.db import update_stats, get_stats
from datetime import datetime
import random
from datetime import timedelta

active_atlas_games = {}
pending_atlas_games = {}

class AtlasGame:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.players = []
        self.starter = None
        self.start_time = None
        self.current_letter = None
        self.used_places = set()
        self.turn_index = 0
        self.time_left = 45
        self.name_length = 3
        self.place_count = 0
        self.consecutive_count = 0

    async def start_countdown(self, delay=60):
        delays = [60, 30, 15, 10]
        for delay in delays:
            if self.chat_id in active_atlas_games:
                return
            if delay == 60:
                await word.send_message(self.chat_id, "🌍 Atlas game is starting in 1 minute - join now!\n\nRules:\n- 45s per place name\n- Start with 3-letter names\n- Every 4 names reduce time by 10s\n- Every 2 names increase length by 1")
            else:
                await word.send_message(self.chat_id, f"Starting game in {delay} seconds...")
            await asyncio.sleep(delay if delay == 60 else delays[delays.index(delay) - delays[delays.index(delay)+1]] if delays.index(delay)+1 < len(delays) else delay)
        if self.chat_id in active_atlas_games:
            return
        if len(self.players) >= 2:
            await self.start_game()
        else:
            await word.send_message(self.chat_id, "Not enough players to start the game!")
            del pending_atlas_games[self.chat_id]

    async def start_game(self):
        self.start_time = datetime.now()
        active_atlas_games[self.chat_id] = self
        del pending_atlas_games[self.chat_id]
        self.current_letter = random.choice('abcdefghijklmnopqrstuvwxyz').upper()
        turn_order = "\n".join([f"• {p['mention']}" for p in self.players])
        await word.send_message(self.chat_id, f"🌏 Atlas Game Started!\n\nFirst letter: **{self.current_letter}**\nTurn order:\n{turn_order}")
        await self.next_turn()

    async def next_turn(self):
        if self.chat_id not in active_atlas_games:
            return
        if not self.players:
            await word.send_message(self.chat_id, "No players left! Ending game.")
            del active_atlas_games[self.chat_id]
            return
        if self.time_left <= 0:
            return await self.handle_timeout()
        player = self.players[self.turn_index]
        cache_total_players = {}
        for p in self.players:
            cache_total_players[p['id']] = p['mention']
        await word.send_message(self.chat_id, 
            f"🌎 Turn: {player['mention']} (Next: {self.players[(self.turn_index+1)%len(self.players)]['mention']})\n"
            f"Place must start with **{self.current_letter.upper()}**\n"
            f"Minimum length: {self.name_length} letters\n"
            f"⏱️ Time left: {self.time_left}s\n"
            f"👥 Players: {len(self.players)}/{len(cache_total_players)}\n"
            f"🔢 Total places: {self.place_count}")
        try:
            answer = await word.listen(filters=filters.user(player['id']) & filters.chat(self.chat_id) & filters.text, timeout=self.time_left)
            await self.validate_place(answer)
        except:
            await self.handle_timeout()

    async def validate_place(self, msg: Message):
        place = msg.text.lower().strip()
        if not place.startswith(self.current_letter.lower()):
            await msg.reply(f"{place.capitalize()} doesn't start with **{self.current_letter.upper()}**!")
            return await self.next_turn()
        if len(place) < self.name_length:
            await msg.reply(f"{place.capitalize()} has less than {self.name_length} letters.")
            return await self.next_turn()
        if place.lower() not in (p.lower() for p in ALL_COUNTRY_SET):
            await msg.reply(f"{place.capitalize()} is not a valid city/state/country!")
            return await self.next_turn()
        if place in self.used_places:
            await msg.reply(f"{place.capitalize()} has been used!")
            return await self.next_turn()
        
        self.used_places.add(place)
        self.current_letter = place[-1].upper()
        self.place_count += 1
        self.consecutive_count += 1
        
        if self.consecutive_count % 4 == 0:
            self.time_left = max(15, self.time_left - 10)
        if self.consecutive_count % 2 == 0:
            self.name_length += 1
            
        await update_stats(msg.from_user.id, "atlas_places", 1)
        await update_stats(msg.from_user.id, "atlas_letters", len(place))
        self.turn_index = (self.turn_index + 1) % len(self.players)
        await word.send_message(self.chat_id, f"__{place.capitalize()}__ accepted! Next letter: **{self.current_letter}**")
        await self.next_turn()

    async def handle_timeout(self):
        player = self.players.pop(self.turn_index)
        if not player:
            del active_atlas_games[self.chat_id]
            return
        await word.send_message(self.chat_id, f"⏰ {player['mention']} ran out of time! Eliminated!")
        if len(self.players) == 1:
            winner = self.players[0]
            duration = datetime.now() - self.start_time
            formatted_duration = str(timedelta(seconds=int(duration.total_seconds())))
            longest = max(self.used_places, key=len) if self.used_places else "N/A"
            await word.send_message(self.chat_id, 
                f"🏆 {winner['mention']} won the Atlas Game!\n"
                f"🌐 Total places: {self.place_count}\n"
                f"📏 Longest place: {longest.capitalize()} ({len(longest)} letters)\n"
                f"⏱️ Duration: {formatted_duration}")
            await update_stats(winner['id'], "atlas_wins", 1)
            for player in self.players:
                await update_stats(player['id'], "atlas_played", 1)
            if longest:
                stats = await get_stats(winner['id'])
                prev_longest = stats.get('atlas_longest', '')
                if len(longest) > len(prev_longest):
                    await update_stats(winner['id'], "atlas_longest", longest)
            del active_atlas_games[self.chat_id]
        else:
            self.turn_index %= len(self.players)
            await self.next_turn()

@word.on_message(filters.command("startatlas") & filters.group)
async def start_atlas(client, message: Message):
    chat_id = message.chat.id
    if chat_id in pending_atlas_games or chat_id in active_atlas_games:
        return await message.reply("An Atlas game is already active/pending!")
    
    game = AtlasGame(chat_id)
    pending_atlas_games[chat_id] = game
    game.starter = message.from_user.id
    game.players.append({
        'id': message.from_user.id,
        'mention': message.from_user.mention
    })
    await message.reply("🌍 Atlas game started! Type /joinatlas to participate!")
    asyncio.create_task(game.start_countdown())

@word.on_message(filters.command("joinatlas") & filters.group)
async def join_atlas(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in pending_atlas_games:
        return await message.reply("No pending Atlas game to join!")
    
    game = pending_atlas_games[chat_id]
    if any(p['id'] == message.from_user.id for p in game.players):
        return await message.reply("You're already in the Atlas game!")
    
    game.players.append({
        'id': message.from_user.id,
        'mention': message.from_user.mention
    })
    await message.reply(f"🌎 {message.from_user.mention} joined the Atlas game!")

@word.on_message(filters.command("fleeatlas") & filters.group)
async def flee_atlas(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in pending_atlas_games and chat_id not in active_atlas_games:
        return await message.reply("No Atlas game to leave!")
    
    if chat_id in pending_atlas_games:
        game = pending_atlas_games[chat_id]
        game.players = [p for p in game.players if p['id'] != message.from_user.id]
        if not game.players:
            del pending_atlas_games[chat_id]
            await message.reply("Atlas game canceled!")
        else:
            await message.reply("You left the Atlas game!")
    elif chat_id in active_atlas_games:
        game = active_atlas_games[chat_id]
        game.players = [p for p in game.players if p['id'] != message.from_user.id]
        await message.reply("You fled the Atlas game!")
        if len(game.players) <= 1:
            await game.handle_timeout()

@word.on_message(filters.command("extendatlas") & filters.group)
async def extend_atlas(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in pending_atlas_games:
        return await message.reply("No pending Atlas game to extend!")
    
    game = pending_atlas_games[chat_id]
    await game.start_countdown(30)
    await message.reply("⏳ Atlas game start extended by 30 seconds!")

@word.on_message(filters.command("atlasstats"))
async def show_atlas_stats(client, message: Message):
    stats = await get_stats(message.from_user.id)
    await message.reply(
        f"🌎 Atlas Stats for {message.from_user.mention}:\n"
        f"• {stats.get('atlas_played', 0)} games played\n"
        f"• {stats.get('atlas_wins', 0)} wins\n"
        f"• {stats.get('atlas_places', 0)} places named\n"
        f"• Longest place: {stats.get('atlas_longest', 'None')}"
    )

@word.on_message(filters.command("forceatlas") & filters.group)
async def force_start_atlas(client, message: Message):
    chat_id = message.chat.id
    if chat_id not in pending_atlas_games:
        return await message.reply("No pending Atlas game to force start!")
    
    game = pending_atlas_games[chat_id]
    if message.from_user.id != game.starter:
        return await message.reply("Only the game starter can force start!")
    
    await game.start_game()