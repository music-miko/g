# -- Full Updated Spyfall Bot Code with 60-Second Explanation Timeout --

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
        self.explanation_timeout_task = None
        self.dead_players = []

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
        self.explanation_timeout_task = asyncio.create_task(self.handle_explanation_timeout(player))

    async def handle_explanation_timeout(self, player):
        await asyncio.sleep(60)
        if self.players[self.current_player_index] == player and player['id'] not in self.explanations:
            self.dead_players.append(player)
            await spy.send_message(self.chat_id, f"💀 {player['mention']} did not respond in 60 seconds and is marked as DEAD.")
            self.current_player_index += 1
            await self.prompt_next_explanation()

    async def handle_explanation(self, user_id, text):
        if user_id != self.players[self.current_player_index]['id']:
            return False
        self.explanations[user_id] = text
        if self.explanation_timeout_task:
            self.explanation_timeout_task.cancel()
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
            f"🚨 {self.get_player(eliminated)['mention'] if eliminated else 'No one'} eliminated!
"
            f"👤 Imposter: {self.imposter['mention']}
"
            f"Common: {self.common_word} | Imposter: {self.imposter_word}
"
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
