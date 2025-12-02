# bot.py
import discord
from discord.ext import commands
import os
import sys
import asyncio

# Ensure project root is on sys.path so packages at repo root (e.g., database, configuration)
# can be imported when running this file as a script: `python src/main.py`.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.database import init_db
from configuration.config import TOKEN

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize database
init_db()

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

async def load_extensions():
    # Load all cogs from the cogs directory
    # Note: We assume this file is in src/main.py and cogs are in src/cogs/
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass