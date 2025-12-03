import discord
from discord.ext import commands
from database.database import get_db
from database.models import Assessment
from mistral_client import ask_mistral

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #==============================================================================================================
    #===============================================>AI ASK<=======================================================
    #==============================================================================================================
    @commands.command()
    async def ask(self, ctx, *, question: str = None):
        # Try local DB first
        if not question:
            await ctx.send('Usage: `!ask <question>`')
            return
        db = get_db()
        try:
            exams = db.query(Assessment).order_by(Assessment.date).all()
            context = "Upcoming exams: " + "; ".join([f"{e.subject} on {e.date}" for e in exams[:5]])
        finally:
            db.close()

        # Try Mistral
        ai_answer = await ask_mistral(question, context)
        if ai_answer:
            await ctx.send(f"🤖 **AI Answer:**\n{ai_answer}")
        else:
            await ctx.send("I couldn't find an answer. Try asking the CR or teacher!")

async def setup(bot):
    await bot.add_cog(AI(bot))
