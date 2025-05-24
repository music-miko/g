# WordGameBot

A Telegram bot for word chain and word guessing games in group chats. Built with Python and Pyrogram.

## Features

- Classic word chain game with turn-based gameplay
- Word guessing game where users can host and guess
- Player statistics tracking
- 466,000+ word dictionary for validation

## Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd WordGameBot
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables
   ```bash
   export TOKEN="your_telegram_bot_token"
   export MONGO_URL="your_mongodb_connection_string"
   export API_HASH="your_telegram_api_hash"
   export API_ID="your_telegram_api_id"
   ```

4. Run the bot
   ```bash
   python -m word
   ```

## Commands

### Classic Word Chain Game
- `/startclassic` - Start a new classic word chain game
- `/join` - Join a pending game
- `/flee` - Leave a pending game
- `/extend` - Extend game start countdown by 30 seconds
- `/forcestart` - Force start the game (starter only)

### Host Word Guessing Game
- `/host` - Start hosting a word guessing game
- `/stopgame` - Stop the current host game (host only)

### General Commands
- `/start` - Bot introduction and add to group
- `/help` - Show help information
- `/stats` - View your personal statistics

## How to Play

### Classic Word Chain Game

1. **Starting a Game**
   - Use `/startclassic` in a group chat
   - Players join with `/join` command
   - Game starts automatically after 1 minute or use `/forcestart`

2. **Game Rules**
   - First word starts with a random letter
   - Each subsequent word must start with the last letter of the previous word
   - Minimum word length starts at 3 letters
   - Each player has 45 seconds per turn
   - Word length increases by 1 every 2 words
   - Time limit decreases by 10 seconds every 4 words

3. **Winning**
   - Last player remaining wins the game
   - Players are eliminated if they run out of time
   - Invalid words result in turn skipping

### Host Word Guessing Game

1. **Hosting**
   - Use `/host` command to start hosting
   - Use inline buttons to see or change the word
   - Players guess by typing words in chat

2. **Guessing**
   - Simply type your guess in the group chat
   - First correct guess wins the round
   - Host cannot participate in guessing


## Deployment

### Heroku Deployment

The bot is ready for Heroku deployment with the included `Procfile`:

```bash
git add .
git commit -m "Deploy WordGameBot"
git push heroku main
```

### Local Development

```bash
python -m word
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This is an open source project and contributions are welcome! Feel free to fork, modify, and distribute according to the MIT License terms.

## Bug Reports

If you encounter any issues:
1. Check existing issues on the repository
2. Create a detailed bug report with steps to reproduce
3. Include bot logs if possible

---

Add the bot to your group: [@WordNWordRobot](https://t.me/WordNWordRobot?startgroup=true)
