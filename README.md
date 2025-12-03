# Class Assistant Bot

A Discord bot to manage class schedules, assignments, notes, and shared materials — with optional AI-powered answers.

This repository contains the Class Assistant Bot used to fetch and present schedules, manage assignments and materials, and provide quick study help via an AI assistant. It supports local development with SQLite and production deployment using PostgreSQL (Supabase) and Render.

## Quick highlights
- Run locally: `python3 src/main.py`
- Run and force import schedule from `main.json`: `python3 src/main.py --override`
- Logs: `bot.log` (contains INFO/DEBUG logs and message-level logs like `message to bot` / `message by bot`)
- Config: environment variables (see below)

## Table of contents
- [Requirements](#requirements)
- [Configuration](#configuration)
- [Running locally](#running-locally)
- [CLI flags](#cli-flags)
- [Commands overview](#commands-overview)
- [Deployment (Render + Supabase)](#deployment-render--supabase)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Requirements
- Python 3.11+ (project uses 3.11 in Dockerfile)
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration
Create a `.env` file at the project root or set these environment variables in your deployment environment.

Required environment variables
- `DISCORD_TOKEN` — Your Discord bot token (required)

Optional/Recommended
- `DATABASE_URL` — PostgreSQL connection URI (when provided, the bot uses PostgreSQL; otherwise it falls back to SQLite)
- `MISTRAL_API_KEY` — API key for the AI assistant integration
- `CR_USER_ID` — (optional) numeric Discord user ID of the Class Representative (CR) — grants CR-only commands
- `CR_ROLE_NAME` — (optional) role name used to mark CRs (default: "Class Representative")
- `ANNOUNCEMENT_CHANNEL_ID` — (optional) channel id for scheduled announcements

Example `.env` (do NOT commit this file):

```env
DISCORD_TOKEN=your_discord_token_here
DATABASE_URL=postgresql://postgres:password@db.supabase.co:5432/postgres
MISTRAL_API_KEY=sk-xxxx
CR_USER_ID=123456789012345678
CR_ROLE_NAME=CR
ANNOUNCEMENT_CHANNEL_ID=987654321012345678
```

The config loader is `src/configuration/config.py` which uses `python-dotenv` to read `.env`.

## Running locally

1. Install dependencies: `pip install -r requirements.txt`
2. Create `.env` with at least `DISCORD_TOKEN` set.
3. Run the bot:

```bash
python3 src/main.py
```

If you want the bot to import the schedule from `main.json` and overwrite any existing schedule in the database, run:

```bash
python3 src/main.py --override
```

Notes
- The bot writes logs to `bot.log` in the project root. Check this file for detailed debug info.
- For development the bot will fall back to SQLite if `DATABASE_URL` is not set.

## CLI flags
- `--override` — Force import of `main.json` into the database (clears existing schedule rows first). If you omit `--override` and the database already has schedule entries the import will be skipped to avoid accidental overwrites.

## Commands overview (quick)
Type `!bothelp` in Discord to get the dynamic help menu. Example commonly used commands:

- `!schedule today` — Today's classes
- `!schedule tomorrow` — Tomorrow's classes
- `!schedule day <day>` — That day's classes
- `!schedule week` — Full week schedule
- `!assignment add Subject="Math" Topic="Algebra" Due="2025-12-01"` — Add assignment
- `!assignment list` — List pending assignments
- `!materials all` — List uploaded materials
- `!materials add Subject="Math" Link="https://..."` — (CR-only) add material
- `!materials delete Subject="Math" Link="https://..."` — (CR-only) delete material
- `!notes <Subject>` — View study notes
- `!ask <question>` — Ask the AI assistant

The bot also supports grouped commands (e.g., `!assignment add/list/delete`) — use `!bothelp <category>` or `!bothelp <command>` for detailed usage.

## Deployment (Render + Supabase)
Full deployment instructions are available in `guides/RENDER_DEPLOYMENT_GUIDE.md` and `guides/SUPABASE_SETUP.md`. A short summary:

1. Create a Supabase project and get your PostgreSQL connection string (set it to `DATABASE_URL` in Render).
2. On Render, create a new **Web Service** (use Docker runtime) and set the environment variables described in [Render guide](https://github.com/KhagendraN/Discord-Bot/blob/main/guides/RENDER_DEPLOYMENT_GUIDE.md).
3. Render will build the Docker image (see `Dockerfile`) and run `./scripts/start.sh` which keeps the process alive.

Notes about persistence
- Use Supabase (PostgreSQL) in production for reliable persistence. If no `DATABASE_URL` is configured the bot will use SQLite for local testing only.

## Logging
- Console: INFO and above
- File: `bot.log` (DEBUG and above)

The bot logs message-level events such as `message to bot: ...` and `message by bot: ...` which helps debug command usage and AI responses.

## Troubleshooting

- Bot fails to start / `ModuleNotFoundError: No module named 'discord'` — ensure you installed the dependencies in the right Python environment (virtualenv/venv).
- `Improper token` or bot offline — verify `DISCORD_TOKEN` value.
- Schedule import overwritten unexpectedly — run without `--override` to preserve DB; use `--override` only when intentional.
- Database connection issues — verify `DATABASE_URL` and check Supabase project and Render environment variables.

## Contributing
- Bug reports and PRs are welcome. Please open issues for feature requests or share deployment notes.

## Useful files
- `src/` — bot source
- `src/cogs/` — command groups (schedule, assignments, AI, etc.)
- `main.json` — main schedule file used for bulk import
- `requirements.txt` — pip deps
- `Dockerfile`, `render.yaml`, `scripts/start.sh` — deployment helpers
- `guides/` — deployment and DB setup guides
