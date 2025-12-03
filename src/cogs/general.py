import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #==============================================================================================================
    #===============================================>HELP<=========================================================
    #==============================================================================================================
    @commands.command(name="bothelp", aliases=["commands"])
    async def bothelp(self, ctx, *, topic: str = None):
        """Show bot help. Without args lists categories and top-level commands.
        Provide a topic (cog name or command) to see detailed commands.
        """
        # Collect top-level commands (ignore hidden)
        top_cmds = [c for c in self.bot.commands if not getattr(c, "parent", None) and not c.hidden]

        # Group by cog name
        cogs = {}
        for cmd in top_cmds:
            cog_name = cmd.cog_name or "General"
            cogs.setdefault(cog_name, []).append(cmd)

        if not topic:
            # Build summary message
            msg_lines = ["**Class Assistant Bot - Available command categories**\n"]
            for cog_name, cmds in sorted(cogs.items()):
                # show cog header and top-level command names
                cmd_list = ", ".join([f"`!{c.name}`" for c in cmds])
                msg_lines.append(f"**{cog_name}:** {cmd_list}")

            msg_lines.append("\nType `!bothelp <category>` or `!bothelp <command>` for details. Example: `!bothelp schedule`")
            await ctx.send("\n".join(msg_lines))
            return

        # Topic provided -> try to match a cog name first
        topic_lower = topic.strip().lower()

        # Match cog
        for cog_name, cmds in cogs.items():
            if cog_name.lower() == topic_lower:
                lines = [f"**{cog_name} commands:**\n"]
                for cmd in sorted(cmds, key=lambda x: x.name):
                    if hasattr(cmd, "commands") and cmd.commands:
                        # it's a Group; list its subcommands
                        lines.append(f"`!{cmd.name}` - {cmd.help or 'Group of related commands.'}")
                        for sc in cmd.commands:
                            if sc.hidden:
                                continue
                            usage = f"!{sc.qualified_name} {sc.signature}".strip()
                            lines.append(f"    • `{usage}` - {sc.help or ''}")
                    else:
                        usage = f"!{cmd.qualified_name} {cmd.signature}".strip()
                        lines.append(f"`{usage}` - {cmd.help or ''}")

                await ctx.send("\n".join(lines))
                return

        # Match a top-level command name
        for cmd in top_cmds:
            if cmd.name.lower() == topic_lower:
                # If it's a group, show subcommands
                if hasattr(cmd, "commands") and cmd.commands:
                    lines = [f"**{cmd.name} (group) commands:**\n", f"{cmd.help or 'Group of related commands.'}"]
                    for sc in cmd.commands:
                        if sc.hidden:
                            continue
                        usage = f"!{sc.qualified_name} {sc.signature}".strip()
                        lines.append(f"• `{usage}` - {sc.help or ''}")
                    await ctx.send("\n".join(lines))
                    return
                else:
                    usage = f"!{cmd.qualified_name} {cmd.signature}".strip()
                    await ctx.send(f"`{usage}` - {cmd.help or 'No description available.'}")
                    return

        # No match found
        await ctx.send("I couldn't find that category or command. Try `!bothelp` to see categories.")

async def setup(bot):
    await bot.add_cog(General(bot))
