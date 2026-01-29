import discord
import io
from discord.ext import commands
import re
from database.database import get_db
from database.models import Assignment, Note, Material
from utils import is_cr

class Assignments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #==============================================================================================================
    #============================================>ASSIGNMENTS<=====================================================
    #==============================================================================================================
    @commands.group(invoke_without_command=True)
    async def assignment(self, ctx):
        await ctx.send("Usage: `!assignment add/list/delete`")

    @assignment.command()
    async def add(self, ctx, *, args: str = None):
        try:
            if not args:
                await ctx.send('Usage: `!assignment add Subject="Math" Topic="Algebra" Due="2025-12-01"`')
                return
            # Robust parsing with regex: Captures Key="Value" or Key='Value'
            matches = re.findall(r'(\w+)="([^\"]*)"|(\w+)=\'([^\']*)\'', args)
            parts = {}
            for match in matches:
                key = match[0] or match[2]
                value = match[1] or match[3]
                parts[key] = value
            
            subject = parts.get("Subject", "").strip()
            topic = parts.get("Topic", "").strip()
            due = parts.get("Due", "").strip()
            
            if not all([subject, topic, due]):
                raise ValueError("Missing fields")
            
            db = get_db()
            try:
                new_assignment = Assignment(subject=subject.title(), topic=topic, due_date=due)
                db.add(new_assignment)
                db.commit()
                await ctx.send(f"Assignment added: **{topic}** for **{subject.title()}**, due **{due}**")
            finally:
                db.close()
        except:
            await ctx.send('Usage: `!assignment add Subject="Math" Topic="Algebra" Due="2025-12-01"`\n\n**Examples that now work:**\n- `Subject="Control system" Topic="Chapter 1" Due="2025-12-01"`\n- `Subject="Math" Topic="Algebra" Due="2025-12-01" `')

    @assignment.command()
    async def list(self, ctx):
        db = get_db()
        try:
            assignments = db.query(Assignment).order_by(Assignment.due_date).all()
            
            if not assignments:
                await ctx.send("No assignments pending.")
                return

            msg = "**Pending Assignments**\n"
            for a in assignments:
                msg += f"{a.id}. **{a.subject}** - {a.topic} (Due: {a.due_date})\n"
            await ctx.send(msg)
        finally:
            db.close()

    @assignment.command()
    @is_cr()
    async def delete(self, ctx, index: int):
        db = get_db()
        try:
            assignment = db.query(Assignment).filter(Assignment.id == index).first()
            if assignment:
                db.delete(assignment)
                db.commit()
                await ctx.send(f"Deleted assignment: {assignment.topic} ({assignment.subject})")
            else:
                await ctx.send("Assignment not found.")
        finally:
            db.close()

    # NOTES (view-only) & MATERIALS (Similar structure)
    @commands.group(invoke_without_command=True)
    async def notes(self, ctx, subject=None):
        """View study notes for a subject. Adding/removing notes is disabled.
    
        Usage: `!notes <Subject>`
        """
        if subject:
            db = get_db()
            try:
                links = db.query(Note).filter(Note.subject == subject.title()).all()
                if links:
                    msg = f"**Study Notes for {subject.title()}**\n"
                    for l in links:
                        msg += f"• {l.link}\n"
                    await ctx.send(msg)
                else:
                    await ctx.send(f"No notes found for **{subject.title()}**")
            finally:
                db.close()
        else:
            await ctx.send("Usage: `!notes <Subject>`")

    # MATERIALS (Google Drive)
    @commands.group(invoke_without_command=True)
    async def materials(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Usage: `!materials [subject]/all/add/delete`\nNote: `add` and `delete` are CR-only commands.")

    @materials.command()
    async def all(self, ctx):
        db = get_db()
        try:
            items = db.query(Material).all()
        except Exception:
            db.close()
            await ctx.send("❌ Failed to read materials from the database.")
            return

        try:
            if not items:
                await ctx.send("No materials uploaded yet.")
                return

            header = "**All Google Drive Materials**\n"
            # Build messages under Discord's 2000 char limit (leave some headroom)
            max_len = 1900
            current = header
            for i in items:
                line = f"• **{i.subject}**: {i.drive_link}\n"
                if len(current) + len(line) > max_len:
                    try:
                        await ctx.send(current)
                    except Exception:
                        # fallback: send as file (use BytesIO)
                        try:
                            bio = io.BytesIO(current.encode('utf-8'))
                            bio.seek(0)
                            await ctx.send(file=discord.File(bio, filename='materials.txt'))
                        except Exception:
                            await ctx.send("❌ Failed to send materials list (message too large).")
                            return
                    current = header + line
                else:
                    current += line

            # send remaining
            try:
                await ctx.send(current)
            except Exception:
                try:
                    bio = io.BytesIO(current.encode('utf-8'))
                    bio.seek(0)
                    await ctx.send(file=discord.File(bio, filename='materials.txt'))
                except Exception:
                    await ctx.send("❌ Failed to send materials list.")
        finally:
            db.close()


    @materials.command()
    @is_cr()
    async def add(self, ctx, *, args: str = None):
        """Add a Google Drive material link. CR-only.
    
        Expected format: Subject="SubjectName" Link="https://drive.link/..."
        """
        if not args:
            await ctx.send('Usage: `!materials add Subject="Math" Link="https://..."`')
            return
        try:
            matches = re.findall(r'(\w+)="([^"]*)"|(\w+)=\'([^\']*)\'', args)
            parts = {}
            for match in matches:
                key = match[0] or match[2]
                value = match[1] or match[3]
                parts[key] = value

            subject = parts.get("Subject", "").strip()
            link = parts.get("Link", "").strip()
            if not subject or not link:
                raise ValueError("Missing Subject or Link")

            db = get_db()
            try:
                new_material = Material(subject=subject.title(), drive_link=link)
                db.add(new_material)
                db.commit()
                await ctx.send(f"✅ Material added for **{subject.title()}**: {link}")
            finally:
                db.close()
        except ValueError as ve:
            await ctx.send(f"❌ {ve}. Usage: `!materials add Subject=\"Math\" Link=\"https://...\"`")
        except Exception:
            await ctx.send("❌ Failed to add material. Ensure command format is correct.")


    @materials.command()
    @is_cr()
    async def delete(self, ctx, *, args: str = None):
        """Delete a material by subject+link. CR-only.
    
        Expected: Subject="Math" Link="https://..."
        """
        # If user didn't provide args, show usage instead of raising a framework error
        if not args:
            await ctx.send('Usage: `!materials delete Subject="Math" Link="https://..."`')
            return
        try:
            matches = re.findall(r'(\w+)="([^"]*)"|(\w+)=\'([^\']*)\'', args)
            parts = {}
            for match in matches:
                key = match[0] or match[2]
                value = match[1] or match[3]
                parts[key] = value

            subject = parts.get("Subject", "").strip()
            link = parts.get("Link", "").strip()
            if not subject or not link:
                raise ValueError("Missing Subject or Link")

            db = get_db()
            try:
                # Find and delete
                # Note: This deletes ALL matching entries.
                rows = db.query(Material).filter(
                    Material.subject == subject.title(),
                    Material.drive_link == link
                ).all()
                
                if rows:
                    for row in rows:
                        db.delete(row)
                    db.commit()
                    await ctx.send(f"✅ Material deleted for **{subject.title()}**")
                else:
                    await ctx.send("⚠️ No matching material found to delete.")
            finally:
                db.close()
        except ValueError as ve:
            await ctx.send(f"❌ {ve}. Usage: `!materials delete Subject=\"Math\" Link=\"https://...\"`")
        except Exception:
            await ctx.send("❌ Failed to delete material. Ensure the format is correct and the material exists.")

async def setup(bot):
    await bot.add_cog(Assignments(bot))
