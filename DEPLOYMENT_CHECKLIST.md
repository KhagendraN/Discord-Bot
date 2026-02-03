# Railway Deployment Checklist

Follow this checklist to deploy your Discord bot to Railway.

## Pre-Deployment

- [ ] **Code is working locally**
  ```bash
  python src/main.py
  ```

- [ ] **All environment variables are documented** in `.env.example`

- [ ] **Code is in a Git repository**
  ```bash
  git init
  git add .
  git commit -m "Initial commit"
  ```

- [ ] **Repository is pushed to GitHub**
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
  git push -u origin main
  ```

## Railway Setup

- [ ] **Create Railway account** at [railway.app](https://railway.app)

- [ ] **Create new project**
  - Click "New Project"
  - Select "Deploy from GitHub repo"
  - Choose your repository

- [ ] **Add environment variables** (Project → Variables):
  ```
  DISCORD_TOKEN=<your_token>
  DATABASE_URL=<supabase_or_railway_postgres>
  MISTRAL_API_KEY=<your_key>
  ANNOUNCEMENT_CHANNEL_ID=<channel_id>
  CR_USER_ID=<user_id>
  CR_ROLE_NAME=Class Representative
  ```

- [ ] **(Optional) Add Railway PostgreSQL**
  - Click "New" → "Database" → "Add PostgreSQL"
  - `DATABASE_URL` will be auto-created
  - Remove Supabase URL if switching

## Verification

- [ ] **Check deployment logs**
  - Go to "Deployments" tab
  - Verify no errors in build logs

- [ ] **Verify bot is online**
  - Check your Discord server
  - Bot should show as online

- [ ] **Test basic commands**
  ```
  !bothelp
  !schedule today
  ```

- [ ] **Monitor logs**
  - Go to "Logs" tab
  - Watch for any errors or warnings

## Post-Deployment

- [ ] **Set up monitoring** (optional)
  - Enable email notifications for crashes
  - Set up uptime monitoring

- [ ] **Document deployment**
  - Note your Railway project URL
  - Save environment variable list

## Troubleshooting

If bot doesn't start:
1. Check "Logs" tab in Railway for errors
2. Verify all environment variables are set
3. Check Discord token is valid
4. Verify DATABASE_URL connection

## Deployment Files Created

✅ `Procfile` - Start command
✅ `railway.json` - Railway configuration
✅ `runtime.txt` - Python version
✅ `.railwayignore` - Files to exclude
✅ `.env.example` - Environment variables template

## Next Steps

After successful deployment:
- Set up automatic deployments (push to GitHub = auto deploy)
- Monitor usage to stay within free tier limits
- Consider upgrading if you need more resources

---

**Need help?** See [guides/RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md) for detailed instructions.
