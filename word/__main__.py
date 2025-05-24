import pyrogram
from word import word

async def run_clients():
    await word.start()
    await pyrogram.idle()

if __name__ == "__main__":
    word.loop.run_until_complete(run_clients())