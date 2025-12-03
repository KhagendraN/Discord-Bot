import discord
from discord.ext import commands
from datetime import datetime, timedelta
from database.database import get_db
from database.models import Schedule as ScheduleModel
from utils import (
    is_cr, get_week_key, load_main_schedule_from_file, save_main_schedule_to_file,
    apply_temp_replacement, apply_temp_cancellation, merge_schedule_for_week,
    apply_temp_changes_to_db_rows, _parse_edit_cancel_args, _normalize_time,
    _normalize_subject, MAIN_SCHEDULE, TEMP_CHANGES
)
import utils

class Schedule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _format_schedule_entry(self, e):
        """Helper to format a single schedule entry."""
        subject = e.get('subject', 'Unknown')
        time = e.get('time', 'Unknown')
        room = e.get('room', '')
        instructor = e.get('instructor', '')
        note = e.get('note', '')
        
        # Parse Type from Subject
        type_str = "Unknown"
        if "(L)" in subject:
            type_str = "Lecture"
        elif "(T)" in subject:
            type_str = "Tutorial"
        elif "(P)" in subject or "Lab" in subject or "Practical" in subject:
            type_str = "Lab"
        elif "(L+T)" in subject:
            type_str = "Lecture + Tutorial"
            
        # Parse Alternate from Note
        alternate = "False"
        if "Alt. week" in note or "Alternate" in note:
            alternate = "True"

        entry_str = f"Subject: {subject}\n"
        entry_str += f"    - time : {time}\n"
        if instructor:
            entry_str += f"    - instructor : {instructor}\n"
        if room:
            entry_str += f"    - room : {room}\n"
        entry_str += f"    - type : {type_str}\n"
        entry_str += f"    - alternate : {alternate}\n"
        entry_str += "-------------------------------------------------------"
        
        return entry_str

    @commands.group(invoke_without_command=True)
    async def schedule(self, ctx):
        await ctx.send("Usage: `!schedule add/delete/today/week`")

    @schedule.command()
    async def today(self, ctx):
        weekday = datetime.now().strftime("%A")
        day_l = weekday.lower()
        
        db = get_db()
        try:
            rows = db.query(ScheduleModel).filter(ScheduleModel.day.ilike(day_l)).all()
            
            week_key = get_week_key()
            merged = apply_temp_changes_to_db_rows(rows, week_key)

            if not merged:
                await ctx.send(f"No classes scheduled for **{weekday}**.")
                return

            msg = f"**{weekday}:**\n"
            msg += "--------------------------------------------------------\n"
            
            grouped = {}
            for e in merged:
                grp = e.get('group_name', 'General')
                if grp not in grouped:
                    grouped[grp] = []
                grouped[grp].append(e)
            
            for grp, entries in grouped.items():
                msg += f"**{grp}:**\n"
                msg += "--------------------------------------------------------\n"
                for e in sorted(entries, key=lambda x: x['time']):
                    msg += self._format_schedule_entry(e) + "\n"

            await ctx.send(msg)
        finally:
            db.close()

    @schedule.command()
    async def tomorrow(self, ctx):
        tomorrow_date = datetime.now() + timedelta(days=1)
        weekday = tomorrow_date.strftime("%A")
        day_l = weekday.lower()
        
        db = get_db()
        try:
            rows = db.query(ScheduleModel).filter(ScheduleModel.day.ilike(day_l)).all()
            
            week_key = get_week_key()
            merged = apply_temp_changes_to_db_rows(rows, week_key)

            if not merged:
                await ctx.send(f"No classes scheduled for **{weekday}**.")
                return

            msg = f"**{weekday}:**\n"
            msg += "--------------------------------------------------------\n"
            
            grouped = {}
            for e in merged:
                grp = e.get('group_name', 'General')
                if grp not in grouped:
                    grouped[grp] = []
                grouped[grp].append(e)
            
            for grp, entries in grouped.items():
                msg += f"**{grp}:**\n"
                msg += "--------------------------------------------------------\n"
                for e in sorted(entries, key=lambda x: x['time']):
                    msg += self._format_schedule_entry(e) + "\n"

            await ctx.send(msg)
        finally:
            db.close()

    @schedule.command()
    async def day(self, ctx, day_name: str):
        day_name = day_name.lower()
        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if day_name not in valid_days:
            await ctx.send("Please provide a valid day of the week (e.g., monday, tuesday, etc.).")
            return
        
        db = get_db()
        try:
            rows = db.query(ScheduleModel).filter(ScheduleModel.day.ilike(day_name)).all()
            
            week_key = get_week_key()
            merged = apply_temp_changes_to_db_rows(rows, week_key)

            if not merged:
                await ctx.send(f"No classes scheduled for **{day_name.capitalize()}**.")
                return

            msg = f"**{day_name.capitalize()}:**\n"
            msg += "--------------------------------------------------------\n"
            
            grouped = {}
            for e in merged:
                grp = e.get('group_name', 'General')
                if grp not in grouped:
                    grouped[grp] = []
                grouped[grp].append(e)
            
            for grp, entries in grouped.items():
                msg += f"**{grp}:**\n"
                msg += "--------------------------------------------------------\n"
                for e in sorted(entries, key=lambda x: x['time']):
                    msg += self._format_schedule_entry(e) + "\n"

            await ctx.send(msg)
        finally:
            db.close()

    @schedule.command()
    async def week(self, ctx):
        days = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        week_key = get_week_key()
        
        db = get_db()
        try:
            msg = ""
            any_entry = False
            for d in days:
                rows = db.query(ScheduleModel).filter(ScheduleModel.day.ilike(d)).all()
                merged = apply_temp_changes_to_db_rows(rows, week_key)
                if merged:
                    any_entry = True
                    day_msg = f"**{d.title()}:**\n"
                    day_msg += "--------------------------------------------------------\n"
                    
                    grouped = {}
                    for e in merged:
                        grp = e.get('group_name', 'General')
                        if grp not in grouped:
                            grouped[grp] = []
                        grouped[grp].append(e)
                    
                    for grp, entries in grouped.items():
                        day_msg += f"**{grp}:**\n"
                        day_msg += "--------------------------------------------------------\n"
                        for e in sorted(entries, key=lambda x: x['time']):
                            day_msg += self._format_schedule_entry(e) + "\n"
                    
                    if len(msg) + len(day_msg) > 1900:
                        await ctx.send(msg)
                        msg = day_msg
                    else:
                        msg += day_msg
            
            if not any_entry:
                await ctx.send("No schedule set yet.")
                return
            
            if msg:
                await ctx.send(msg)
        finally:
            db.close()

    @schedule.command()
    @is_cr()
    async def delete(self, ctx, day: str, time: str, *, subject: str):
        db = get_db()
        try:
            rows = db.query(ScheduleModel).filter(
                ScheduleModel.day == day.title(),
                ScheduleModel.time == time,
                ScheduleModel.subject == subject.title()
            ).all()
            
            if rows:
                for row in rows:
                    db.delete(row)
                db.commit()
                await ctx.send(f"Deleted: {subject.title()} on {day.title()} at {time}")
            else:
                await ctx.send("No matching class found.")
        finally:
            db.close()

    @schedule.command(name='main')
    @is_cr()
    async def schedule_main(self, ctx, subcmd: str, *, filename: str):
        if subcmd.lower() != 'routine':
            await ctx.send("Usage: `!schedule main routine \"assets/main.json\"`")
            return
        filename = filename.strip('"').strip("'")
        try:
            schedule_data = load_main_schedule_from_file(filename)
            
            db = get_db()
            try:
                db.query(ScheduleModel).delete()
                
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
                db.commit()
                await ctx.send(f"✅ Main schedule loaded successfully from `{filename}` and written to database.")
            finally:
                db.close()
        except FileNotFoundError:
            await ctx.send(f"❌ File not found: `{filename}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to load schedule: {e}")

    @schedule.command()
    @is_cr()
    async def edit(self, ctx, *, args: str = None):
        """Edit a class time/subject. Usage:
        !schedule edit GroupA monday 9:00 AM Math 10:00 AM Math permanent|temporary
        """
        if not args:
            await ctx.send("❌ Invalid format. Usage: `!schedule edit GroupA monday 9:00 AM Math 10:00 AM Math permanent` (use 'temporary' or 'permanent')")
            return
        parsed = _parse_edit_cancel_args(args)
        if not parsed or 'new_time' not in parsed:
            await ctx.send("❌ Invalid format. Usage: `!schedule edit GroupA monday 9:00 AM Math 10:00 AM Math permanent` (use 'temporary' or 'permanent')")
            return

        group = parsed['group']
        day = parsed['day']
        orig_time = parsed['orig_time']
        orig_subject = parsed['orig_subject']
        new_time = parsed['new_time']
        new_subject = parsed['new_subject']
        permanent = parsed['permanent']

        if not utils.MAIN_SCHEDULE:
            await ctx.send("❌ No main schedule loaded. Use `!schedule main routine \"main.json\"` first.")
            return

        if permanent:
            group_data = utils.MAIN_SCHEDULE.get(group)
            if not group_data or day not in group_data:
                await ctx.send("⚠️ Group or day not found in main schedule.")
                return
            entries = group_data[day]
            for e in entries:
                if _normalize_time(e.get('time')) == _normalize_time(orig_time) and _normalize_subject(e.get('subject')) == _normalize_subject(orig_subject):
                    e['time'] = new_time
                    e['subject'] = new_subject
                    try:
                        save_main_schedule_to_file()
                        await ctx.send(f"✅ Schedule for {group} on {day.title()} updated permanently: {orig_time} {orig_subject} -> {new_time} {new_subject}")
                    except Exception as ex:
                        await ctx.send(f"❌ Failed to save main schedule: {ex}")
                    return
            await ctx.send("⚠️ Matching class not found in main schedule.")
        else:
            wk = get_week_key()
            apply_temp_replacement(wk, group, day, orig_time, orig_subject, {'time': new_time, 'subject': new_subject, 'room': ''})
            await ctx.send(f"✅ Schedule for {group} on {day.title()} {orig_time} {orig_subject} has been temporarily changed to {new_time} {new_subject} for this week.")

    @schedule.command()
    @is_cr()
    async def cancel(self, ctx, *, args: str = None):
        """Cancel a class. Usage: !schedule cancel GroupA monday 9:00 AM Math permanent|temporary"""
        if not args:
            await ctx.send("❌ Invalid format. Usage: `!schedule cancel GroupA monday 9:00 AM Math permanent`")
            return
        parsed = _parse_edit_cancel_args(args)
        if not parsed:
            await ctx.send("❌ Invalid format. Usage: `!schedule cancel GroupA monday 9:00 AM Math permanent`")
            return

        group = parsed['group']
        day = parsed['day']
        orig_time = parsed['orig_time']
        orig_subject = parsed['orig_subject']
        permanent = parsed.get('permanent', False)

        if permanent:
            if not utils.MAIN_SCHEDULE:
                await ctx.send("❌ No main schedule loaded.")
                return
            group_data = utils.MAIN_SCHEDULE.get(group)
            if not group_data or day not in group_data:
                await ctx.send("⚠️ Group or day not found in main schedule.")
                return
            entries = group_data[day]
            for i, e in enumerate(entries):
                if _normalize_time(e.get('time')) == _normalize_time(orig_time) and _normalize_subject(e.get('subject')) == _normalize_subject(orig_subject):
                    entries.pop(i)
                    try:
                        save_main_schedule_to_file()
                        await ctx.send(f"✅ {orig_subject} on {day.title()} at {orig_time} permanently cancelled for {group}.")
                    except Exception as ex:
                        await ctx.send(f"❌ Failed to save main schedule: {ex}")
                    return
            await ctx.send("⚠️ Matching class not found in main schedule.")
        else:
            wk = get_week_key()
            apply_temp_cancellation(wk, group, day, orig_time, orig_subject)
            await ctx.send(f"✅ {orig_subject} on {day.title()} at {orig_time} temporarily cancelled for {group} this week.")

    @schedule.command()
    async def view(self, ctx, group: str, day: str):
        if not utils.MAIN_SCHEDULE:
            await ctx.send("❌ No main schedule loaded. Use `!schedule main routine \"main.json\"` first.")
            return
        day_l = day.lower()
        week_key = get_week_key()
        merged = merge_schedule_for_week(group, day_l, week_key)
        if not merged:
            await ctx.send(f"No schedule found for **{group}** on **{day.title()}**")
            return
        msg = f"**{group} schedule for {day.title()} (week {week_key[1]})**\n"
        for e in merged:
            msg += self._format_schedule_entry(e) + "\n"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Schedule(bot))
