import discord
from discord.ext import commands
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.database import get_db
from database.models import Assessment
from configuration.config import CHANNEL_ID

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        # Add job if not already present (though in a cog, we usually just add it on load)
        if not self.scheduler.get_job("daily_reminder"):
            self.scheduler.add_job(self.daily_assessment_reminder, 'cron', hour=18, minute=0, id="daily_reminder")

    async def daily_assessment_reminder(self):
        today = datetime.now().strftime("%Y-%m-%d")
        db = get_db()
        try:
            assessments = db.query(Assessment).filter(Assessment.date == today).all()
            
            if assessments and CHANNEL_ID:
                channel = self.bot.get_channel(CHANNEL_ID)
                if channel:
                    msg = "**🔔 Today's Assessments Reminder**\n\n"
                    for a in assessments:
                        time = a.time or "Time not set"
                        desc = a.description or "No description"
                        msg += f"• **{a.subject}**: {desc} at {time}\n"
                    await channel.send("@Class\n" + msg)
        finally:
            db.close()

    def cog_unload(self):
        self.scheduler.shutdown()

async def setup(bot):
    await bot.add_cog(Tasks(bot))
