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

from database.database import init_db, get_db
from database.models import Schedule as ScheduleModel
from configuration.config import TOKEN
from utils import load_main_schedule_from_file

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize database
init_db()

# Auto-import schedule from main.json on startup
def auto_import_schedule():
    """Automatically import schedule from main.json, overriding any existing data."""
    try:
        # Try multiple possible locations for main.json
        possible_paths = [
            os.path.join(PROJECT_ROOT, 'main.json'),  # /app/main.json
            os.path.join(os.path.dirname(__file__), '..', 'main.json'),  # relative to src
            '/app/main.json',  # absolute path in Docker
            'main.json',  # current directory
        ]
        
        print(f"🔍 Looking for main.json...")
        print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
        print(f"   Current dir: {os.getcwd()}")
        
        main_json_path = None
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            print(f"   Checking: {abs_path}")
            if os.path.exists(abs_path):
                main_json_path = abs_path
                print(f"   ✅ Found at: {abs_path}")
                break
        
        if not main_json_path:
            print(f"❌ main.json not found in any of these locations:")
            for path in possible_paths:
                print(f"   - {os.path.abspath(path)}")
            return
        
        print(f"📅 Importing schedule from {main_json_path}...")
        schedule_data = load_main_schedule_from_file(main_json_path)
        
        db = get_db()
        try:
            # Clear existing schedule data
            deleted_count = db.query(ScheduleModel).delete()
            print(f"🗑️ Cleared {deleted_count} existing schedule entries")
            
            # Insert new data from main.json
            entry_count = 0
            for group, days in schedule_data.items():
                for day, entries in days.items():
                    for e in entries:
                        new_entry = ScheduleModel(
                            day=day.title(),
                            time=e.get('time'),
                            subject=e.get('subject'),
                            group_name=group,
                            room=e.get('room', ''),
                            instructor=e.get('instructor', ''),
                            note=e.get('note', '')
                        )
                        db.add(new_entry)
                        entry_count += 1
            db.commit()
            print(f"✅ Schedule imported successfully! ({entry_count} entries)")
        finally:
            db.close()
    except Exception as e:
        print(f"❌ Error auto-importing schedule: {e}")
        import traceback
        traceback.print_exc()

# Run auto-import
auto_import_schedule()

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