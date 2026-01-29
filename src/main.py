#!/usr/bin/env python3
"""Bot entrypoint.

Supports optional --override flag to control whether schedule import from main.json
overwrites the database.

Also configures logging and logs incoming messages ("message to bot") and messages
sent by the bot ("message by bot").
"""
import argparse
import logging
import os
import sys
import asyncio
import discord
from discord.ext import commands

# Ensure project root is on sys.path so packages at repo root (e.g., database, configuration)
# can be imported when running this file as a script: `python src/main.py`.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.database import init_db, get_db
from database.models import Schedule as ScheduleModel
from configuration.config import TOKEN
from utils import load_main_schedule_from_file


# ----- Logging setup -----------------------------------------------------
logger = logging.getLogger('discord_bot')
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(fmt)
fh = logging.FileHandler('/tmp/bot.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(fmt)
logger.addHandler(ch)
logger.addHandler(fh)


# ----- Bot setup ---------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# Initialize database



def auto_import_schedule(override: bool = False):
    """Import schedule from main.json.

    If override is False, do not import when Schedule table already has rows.
    If override is True, clear existing schedule entries and import.
    """
    try:
        # Try multiple possible locations for main.json
        possible_paths = [
            os.path.join(PROJECT_ROOT, 'main.json'),
            os.path.join(os.path.dirname(__file__), '..', 'main.json'),
            '/app/main.json',
            'main.json',
        ]

        logger.debug("🔍 Looking for main.json...")
        logger.debug(f"   PROJECT_ROOT: {PROJECT_ROOT}")
        logger.debug(f"   Current dir: {os.getcwd()}")

        main_json_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            logger.debug(f"   Checking: {abs_path}")
            if os.path.exists(abs_path):
                main_json_path = abs_path
                logger.info(f"   ✅ Found at: {abs_path}")
                break

        if not main_json_path:
            logger.warning("❌ main.json not found in any of these locations:")
            for path in possible_paths:
                logger.warning(f"   - {os.path.abspath(path)}")
            return

        logger.info(f"📅 Importing schedule from {main_json_path}...")
        schedule_data = load_main_schedule_from_file(main_json_path)

        db = get_db()
        try:
            # If not overriding, and DB already has schedule rows, skip import
            if not override:
                existing = db.query(ScheduleModel).count()
                if existing > 0:
                    logger.info(f"Found {existing} existing schedule entries in DB; skipping import (use --override to replace).")
                    return

            # Clear existing schedule data (when override True or DB empty)
            deleted_count = db.query(ScheduleModel).delete()
            logger.info(f"🗑️ Cleared {deleted_count} existing schedule entries")

            # Insert new data from main.json
            entry_count = 0
            for group, days in schedule_data.items():
                # skip any top-level keys that are not schedule groups (e.g., metadata)
                if not isinstance(days, dict):
                    continue
                for day, entries in days.items():
                    # entries should be a list of dicts; skip otherwise
                    if not isinstance(entries, list):
                        continue
                    for e in entries:
                        if not isinstance(e, dict):
                            continue
                        new_entry = ScheduleModel(
                            day=day.title(),
                            time=e.get('time'),
                            subject=e.get('subject'),
                            group_name=group,
                            room=e.get('room', ''),
                            instructor=e.get('instructor', ''),
                            note=e.get('note', ''),
                        )
                        db.add(new_entry)
                        entry_count += 1
            db.commit()
            logger.info(f"✅ Schedule imported successfully! ({entry_count} entries)")
        finally:
            db.close()
    except Exception as e:
        logger.exception(f"❌ Error auto-importing schedule: {e}")


@bot.event
async def on_ready():
    logger.info(f"{bot.user} is online!")


@bot.event
async def on_command_error(ctx, error):
    # Global handler for command errors to ensure they are logged and user is notified
    try:
        # Handle missing required argument gracefully
        if isinstance(error, commands.MissingRequiredArgument):
            param = error.param.name if hasattr(error, 'param') else 'argument'
            usage = ''
            if ctx.command:
                usage = f" Usage: `!{ctx.command.qualified_name} {ctx.command.signature}`"
            await ctx.send(f"❌ Missing required argument: `{param}`.{usage}")
            logger.warning(f"Missing argument in command {ctx.command}: {param}")
            return

        logger.exception(f"Error in command '{getattr(ctx, 'command', None)}': {error}")
        # Friendly message to channel
        await ctx.send("❌ An error occurred while processing your command. The error has been logged.")
    except Exception:
        logger.exception("Failed in on_command_error handler")


@bot.event
async def on_message(message: discord.Message):
    try:
        # Ignore webhooks
        if getattr(message, 'webhook_id', None) is not None:
            return

        if message.author == bot.user:
            # message by bot
            logger.info(f"message by bot: channel={getattr(message.channel, 'name', message.channel.id)} content={message.content}")
        else:
            # message to bot
            logger.info(f"message to bot: author={message.author} channel={getattr(message.channel, 'name', message.channel.id)} content={message.content}")

        # ensure commands still processed
        await bot.process_commands(message)
    except Exception:
        logger.exception("Error in on_message handler")


async def load_extensions():
    # Load all cogs from the cogs directory
    cogs_dir = os.path.join(os.path.dirname(__file__), 'cogs')
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main(argv=None):
    parser = argparse.ArgumentParser(description='Start the Discord bot')
    parser.add_argument('--override', action='store_true', help='Override existing schedule data in DB with main.json')
    args = parser.parse_args(argv)

    # Initialize database
    try:
        init_db()
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error("   Check your DATABASE_URL in .env or Supabase credentials.")
        sys.exit(1)

    # Import schedule according to flag
    try:
        auto_import_schedule(override=args.override)
    except Exception:
        logger.exception('Auto-import schedule failed')

    # Start bot
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        logger.info('Shutting down (KeyboardInterrupt)')
    except Exception:
        logger.exception('Fatal error in main')
    