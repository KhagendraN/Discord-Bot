import os
import json
import re
from datetime import datetime
from discord.ext import commands
from configuration.config import CR_USER_ID, CR_ROLE_NAME

# Global State
MAIN_SCHEDULE = {}
MAIN_SCHEDULE_FILE = None
TEMP_CHANGES = {}

# Ensure project root is on sys.path so packages at repo root (e.g., database, configuration)
# can be imported when running this file as a script: `python src/main.py`.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def is_cr():
    async def predicate(ctx):
        if CR_USER_ID and ctx.author.id == CR_USER_ID:
            return True
        if any(role.name == CR_ROLE_NAME for role in ctx.author.roles):
            return True
        await ctx.send("❌ You don't have permission to use this command.")
        return False
    return commands.check(predicate)

def get_week_key(dt=None):
    d = dt or datetime.now()
    iso = d.isocalendar()
    return (iso.year, iso.week)

def load_main_schedule_from_file(path):
    global MAIN_SCHEDULE, MAIN_SCHEDULE_FILE
    # Resolve path: allow passing a filename relative to project root (where main.json usually lives)
    candidate_paths = []
    # expand user + absolute
    p = os.path.expanduser(path)
    if not os.path.isabs(p):
        p = os.path.abspath(p)
    candidate_paths.append(p)
    # also try relative to project root (one level up from src)
    try:
        pr = PROJECT_ROOT
    except NameError:
        pr = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    candidate_paths.append(os.path.join(pr, path))
    candidate_paths.append(os.path.join(pr, 'assets', path))
    candidate_paths.append(os.path.join(pr, 'assets', os.path.basename(path)))
    candidate_paths.append(os.path.abspath(os.path.join(os.path.dirname(__file__), path)))

    found = None
    for cp in candidate_paths:
        if os.path.isfile(cp):
            found = cp
            break
    if not found:
        raise FileNotFoundError(f"Schedule file not found: {path}. Tried: {', '.join(candidate_paths)}")
    with open(found, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Normalize day keys to lowercase
    normalized = {}
    for group, days in data.items():
        normalized[group] = {}
        for day, entries in days.items():
            normalized[group][day.lower()] = entries
    MAIN_SCHEDULE = normalized
    MAIN_SCHEDULE_FILE = found
    return MAIN_SCHEDULE

def save_main_schedule_to_file(path=None):
    global MAIN_SCHEDULE, MAIN_SCHEDULE_FILE
    if path is None:
        path = MAIN_SCHEDULE_FILE
    if not path:
        raise ValueError("No main schedule file set")
    # We will write days as they are in MAIN_SCHEDULE (lowercase days)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(MAIN_SCHEDULE, f, indent=2, ensure_ascii=False)

def _normalize_time(t):
    if not t:
        return ''
    s = str(t).strip()
    # Ensure there's a space before AM/PM if present (e.g., '9:00AM' -> '9:00 AM')
    s = re.sub(r'\s*([AaPp][Mm])$', r' \1', s)
    # Normalize spacing and AM/PM case
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'([AaPp][Mm])', lambda m: m.group(1).upper(), s)
    return s

def _normalize_subject(sub):
    if not sub:
        return ''
    return str(sub).strip().lower()

def apply_temp_replacement(week_key, group, day, orig_time, orig_subject, new_entry):
    # store normalized keys for robust matching
    ot = _normalize_time(orig_time)
    osub = _normalize_subject(orig_subject)
    # normalize new_entry time/subject for consistency
    new_e = dict(new_entry)
    if 'time' in new_e:
        new_e['time'] = _normalize_time(new_e['time'])
    if 'subject' in new_e:
        new_e['subject'] = new_e['subject'].strip()
    TEMP_CHANGES.setdefault(week_key, {}).setdefault(group, {}).setdefault(day, {}).setdefault('replacements', []).append(((ot, osub), new_e))

def apply_temp_cancellation(week_key, group, day, orig_time, orig_subject):
    ot = _normalize_time(orig_time)
    osub = _normalize_subject(orig_subject)
    TEMP_CHANGES.setdefault(week_key, {}).setdefault(group, {}).setdefault(day, {}).setdefault('cancellations', []).append((ot, osub))

def merge_schedule_for_week(group, day, week_key=None):
    """Return a list of schedule entries for the given group and day, applying temporary changes for the week_key if present."""
    week_key = week_key or get_week_key()
    base = []
    if group in MAIN_SCHEDULE and day in MAIN_SCHEDULE[group]:
        # clone base entries
        base = [dict(e) for e in MAIN_SCHEDULE[group][day]]
    # Apply temporary changes if any
    wk = TEMP_CHANGES.get(week_key, {})
    grp = wk.get(group, {})
    day_changes = grp.get(day, {})
    cancels = set(day_changes.get('cancellations', []))
    replacements = {k: v for (k, v) in day_changes.get('replacements', [])}

    merged = []
    handled_orig_keys = set()

    for e in base:
        key = (_normalize_time(e.get('time')), _normalize_subject(e.get('subject')))
        # If original time+subject canceled directly, skip
        if key in cancels:
            handled_orig_keys.add(key)
            continue

        # If there is a replacement mapping for this original, check if the replacement itself is canceled
        if key in replacements:
            new_e = replacements[key]
            new_key = (_normalize_time(new_e.get('time')), _normalize_subject(new_e.get('subject')))
            # If replacement is canceled explicitly, skip (neither original nor replacement)
            if new_key in cancels:
                handled_orig_keys.add(key)
                continue
            merged.append({
                'time': new_e.get('time'),
                'subject': new_e.get('subject'),
                'room': new_e.get('room', ''),
                'instructor': new_e.get('instructor', ''),
                'note': new_e.get('note', '')
            })
            handled_orig_keys.add(key)
        else:
            # keep original (normalize time for consistent display)
            merged.append({
                'time': _normalize_time(e.get('time')),
                'subject': e.get('subject'),
                'room': e.get('room', ''),
                'instructor': e.get('instructor', ''),
                'note': e.get('note', '')
            })

    # Add any replacement entries that did not map to an existing original (standalone adds)
    for (orig_k, new_e) in day_changes.get('replacements', []):
        if orig_k not in handled_orig_keys:
            new_key = (_normalize_time(new_e.get('time')), _normalize_subject(new_e.get('subject')))
            if new_key in cancels:
                # this standalone replacement was later canceled
                continue
            merged.append({
                'time': new_e.get('time'),
                'subject': new_e.get('subject'),
                'room': new_e.get('room', ''),
                'instructor': new_e.get('instructor', ''),
                'note': new_e.get('note', '')
            })

    return merged

def apply_temp_changes_to_db_rows(rows, week_key):
    """Given a list of sqlite Row-like dicts with keys day,time,subject,group_name,room,
    apply temporary changes from TEMP_CHANGES for week_key and return merged list.
    """
    # build mapping of replacements and cancellations for groups/days
    result = []
    if not rows:
        return []

    def _rget(r, key, default=None):
        try:
            # SQLAlchemy object access
            if hasattr(r, key):
                return getattr(r, key)
            # Dictionary access
            elif hasattr(r, 'get'):
                return r.get(key, default)
            else:
                return r[key]
        except Exception:
            return default

    # Group rows by (group, day) so we can apply replacements/cancellations per group/day
    grouped = {}
    for r in rows:
        group = _rget(r, 'group_name') or _rget(r, 'group') or ''
        day = (_rget(r, 'day') or '').lower()
        grouped.setdefault((group, day), []).append(r)

    wk = TEMP_CHANGES.get(week_key, {})

    # Process each group/day present in DB rows
    for (group, day), rlist in grouped.items():
        # get changes for this group/day
        grp = wk.get(group, {})
        day_changes = grp.get(day, {})
        cancels = set(day_changes.get('cancellations', []))
        replacements = {k: v for (k, v) in day_changes.get('replacements', [])}

        handled_orig_keys = set()

        for r in rlist:
            time = _rget(r, 'time')
            subject = _rget(r, 'subject')
            key = (_normalize_time(time), _normalize_subject(subject))

            if key in cancels:
                # skip cancelled original
                handled_orig_keys.add(key)
                continue

            if key in replacements:
                new_e = replacements[key]
                handled_orig_keys.add(key)
                merged_entry = {
                    'time': new_e.get('time'),
                    'subject': new_e.get('subject'),
                    'room': new_e.get('room', _rget(r, 'room', '')),
                    'group_name': group
                }
                result.append(merged_entry)
            else:
                # keep original (normalize time for consistent display)
                result.append({'time': _normalize_time(time), 'subject': subject, 'room': _rget(r, 'room', ''), 'group_name': group})

        # Add any replacement entries that did not map to an existing original (standalone adds)
        for (orig_k, new_e) in day_changes.get('replacements', []):
            if orig_k not in handled_orig_keys:
                # This replacement did not correspond to any existing row - append as new
                result.append({'time': new_e.get('time'), 'subject': new_e.get('subject'), 'room': new_e.get('room', ''), 'group_name': group})

    # Also process any TEMP_CHANGES for groups/days not present in DB rows (pure adds)
    for grp_name, groups in wk.items():
        for dname, dchanges in groups.items():
            if (grp_name, dname) in grouped:
                continue
            # no DB rows for this group/day; add all replacements that are not cancellations
            for (orig_k, new_e) in dchanges.get('replacements', []):
                result.append({'time': new_e.get('time'), 'subject': new_e.get('subject'), 'room': new_e.get('room',''), 'group_name': grp_name})

    return result

def _find_time_tokens(tokens, start=0):
    """Find a time token starting at or after start. Returns (time_string, start_index, end_index).
    Supports formats like '9:00', '9:00 AM', '09:00', '9:00PM' etc.
    """
    ampm = set(['AM', 'PM', 'am', 'pm'])
    time_re = re.compile(r'^\d{1,2}:\d{2}([AaPp][Mm])?$')
    for i in range(start, len(tokens)):
        t = tokens[i]
        # token like 9:00 or 9:00AM
        if time_re.match(t):
            return (t, i, i)
        # token like 9:00 and next token AM/PM
        if i + 1 < len(tokens) and re.match(r'^\d{1,2}:\d{2}$', t) and tokens[i+1] in ampm:
            return (f"{t} {tokens[i+1]}", i, i+1)
    return (None, -1, -1)

def _parse_edit_cancel_args(args):
    tokens = args.split()
    if len(tokens) < 4:
        return None
    group = tokens[0]
    day = tokens[1].lower()
    # find first time token
    t1, t1s, t1e = _find_time_tokens(tokens, 2)
    if not t1:
        return None
    # find second time token after t1e+1 (for edit). For cancel, second time may not exist.
    t2, t2s, t2e = _find_time_tokens(tokens, t1e+1)
    # mode is last token if it's 'permanent' or 'temporary'
    mode = tokens[-1].lower() if tokens[-1].lower() in ('permanent', 'temporary') else 'temporary'

    if t2:
        # edit: subject is between t1e+1 and t2s-1; new_subject is between t2e+1 and -1 (mode)
        orig_subject = ' '.join(tokens[t1e+1:t2s]).strip()
        new_time = t2
        new_subject = ' '.join(tokens[t2e+1:-1]).strip()
        return {
            'group': group, 'day': day, 'orig_time': t1, 'orig_subject': orig_subject,
            'new_time': new_time, 'new_subject': new_subject, 'permanent': (mode == 'permanent')
        }
    else:
        # cancel: subject is remaining tokens after t1e
        orig_subject = ' '.join(tokens[t1e+1: -1]).strip() if mode in ('permanent', 'temporary') else ' '.join(tokens[t1e+1:]).strip()
        return {
            'group': group, 'day': day, 'orig_time': t1, 'orig_subject': orig_subject, 'permanent': (mode == 'permanent')
        }
