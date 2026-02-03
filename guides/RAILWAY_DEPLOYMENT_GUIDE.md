# Railway Deployment Guide

This guide will help you deploy your Discord bot to Railway.app.

## Why Railway?

- ✅ **Free tier available** (500 hours/month)
- ✅ **Supports Discord bots** (outbound connections allowed)
- ✅ **Easy deployment** from GitHub
- ✅ **Environment variables** management
- ✅ **Persistent storage** with PostgreSQL
- ✅ **Auto-restarts** on failure

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Railway account (sign up at [railway.app](https://railway.app))
4. Your Discord bot token
5. Your Supabase credentials (or Railway PostgreSQL)

## Step-by-Step Deployment

### 1. Push Your Code to GitHub

```bash
# If you haven't initialized git yet
git init
git add .
git commit -m "Initial commit - Discord bot"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 2. Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your GitHub account

### 3. Create a New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your Discord bot repository
4. Railway will automatically detect it's a Python project

### 4. Add Environment Variables

Click on your project → Variables → Add Variables:

**Required Variables:**
```
DISCORD_TOKEN=your_discord_bot_token_here
DATABASE_URL=your_supabase_database_url
MISTRAL_API_KEY=your_mistral_api_key
ANNOUNCEMENT_CHANNEL_ID=your_channel_id
CR_USER_ID=your_user_id
CR_ROLE_NAME=Class Representative
```

**Supabase DATABASE_URL Format:**
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
```

### 5. (Optional) Add Railway PostgreSQL

If you want to use Railway's built-in PostgreSQL instead of Supabase:

1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically create a `DATABASE_URL` variable
3. Remove your Supabase `DATABASE_URL` if you're switching

### 6. Deploy

Railway will automatically:
1. Detect Python 3.11 from `runtime.txt`
2. Install dependencies from `requirements.txt`
3. Run the start command from `Procfile` or `railway.json`

### 7. Monitor Your Bot

1. Go to the "Deployments" tab to see deployment logs
2. Check the "Metrics" tab for CPU/memory usage
3. View live logs in the "Logs" tab

## Deployment Files Explained

### `Procfile`
Tells Railway what command to run:
```
worker: python src/main.py
```

### `railway.json`
Railway configuration (optional):
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python src/main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `runtime.txt`
Specifies Python version:
```
python-3.11.9
```

## Troubleshooting

### Bot Not Starting

1. **Check logs**: Go to your Railway project → Logs
2. **Verify environment variables**: Make sure all required vars are set
3. **Check Discord token**: Ensure it's valid and not expired

### Database Connection Issues

```bash
# Test your DATABASE_URL format
# Should be: postgresql://user:password@host:port/database
```

### Bot Crashes on Startup

- Check if `DISCORD_TOKEN` is set correctly
- Verify `DATABASE_URL` is accessible
- Check logs for specific error messages

### Memory Issues

Railway free tier has 512MB RAM limit. If your bot exceeds this:
- Upgrade to Railway's Pro plan ($5/month)
- Or optimize your code to use less memory

## Updating Your Bot

Just push to GitHub:
```bash
git add .
git commit -m "Update bot features"
git push
```

Railway will automatically detect changes and redeploy!

## Railway CLI (Optional)

Install Railway CLI for local development:

```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run locally with Railway environment variables
railway run python src/main.py
```

## Cost Estimates

**Free Tier:**
- 500 execution hours/month
- $5 credit/month
- Perfect for small Discord bots

**If You Exceed Free Tier:**
- ~$0.000231/minute ($0.01386/hour)
- About $10/month for 24/7 operation

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

## Environment Variables Quick Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | `YOUR_BOT_TOKEN_HERE` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `MISTRAL_API_KEY` | Mistral AI API key | `your_mistral_api_key` |
| `ANNOUNCEMENT_CHANNEL_ID` | Discord channel ID for announcements | `1234567890123456789` |
| `CR_USER_ID` | Class Representative user ID | `9876543210987654321` |
| `CR_ROLE_NAME` | Name of CR role | `Class Representative` |

---

**Your bot should now be running 24/7 on Railway! 🚀**
