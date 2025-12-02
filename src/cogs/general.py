import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #==============================================================================================================
    #===============================================>HELP<=========================================================
    #==============================================================================================================
    @commands.command()
    async def bothelp(self, ctx):
        help_text = """
**Class Assistant Bot Commands**

`!schedule today` - Today's classes
`!schedule tomorrow` - Tomorrow's classes
`!schedule day <day_name>` - That day's classes
`!schedule week` - Full week schedule
`!assignment list` - Pending assignments
`!notes <Subject>` - View notes
`!materials all` - View drive materials
`!ask <question>` - Ask AI about studies/exams

**CR Only:**
`!schedule add/edit/cancel`
`!assignment add/delete`
`!materials add/delete`
`!schedule main routine "file.json"`
"""
        await ctx.send(help_text)

async def setup(bot):
    await bot.add_cog(General(bot))
