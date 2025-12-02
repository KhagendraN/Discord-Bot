# Supabase PostgreSQL Setup Guide

This guide shows you how to set up a **free PostgreSQL database** on Supabase for your Discord bot.

## Why Supabase?
- **Free tier**: 500MB database storage
- **Always online**: Database never sleeps
- **PostgreSQL**: Industry-standard, reliable database
- **Easy setup**: Takes less than 5 minutes

## Step 1: Create a Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click **Start your project**
3. Sign up with GitHub (recommended) or email

## Step 2: Create a New Project

1. Click **New Project**
2. Fill in the details:
   - **Name**: `class-assistant-bot` (or any name)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you (e.g., Singapore, Mumbai)
   - **Pricing Plan**: Free
3. Click **Create new project**
4. Wait 1-2 minutes for the database to be provisioned

## Step 3: Get Your Database Connection String

1. In your Supabase project dashboard, click **Settings** (gear icon in sidebar)
2. Click **Database** in the left menu
3. Scroll down to **Connection string**
4. Select **URI** tab
5. Copy the connection string. It looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```
6. **Important**: Replace `[YOUR-PASSWORD]` with the actual password you created in Step 2

## Step 4: Add to Render Environment Variables

1. Go to your Render dashboard
2. Select your web service (`class-assistant-bot`)
3. Click **Environment** in the left sidebar
4. Click **Add Environment Variable**
5. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste your connection string from Step 3
6. Click **Save Changes**

Render will automatically redeploy your service with the new database connection.

## Step 5: Verify It's Working

1. Wait for Render to finish deploying
2. Check the logs in Render dashboard
3. You should see "Service is live" and no database errors
4. Test your bot in Discord - try adding an assignment or schedule

## Troubleshooting

**Connection Error**: 
- Double-check the password in your connection string
- Make sure there are no extra spaces

**Tables Not Created**:
- The bot automatically creates tables on first startup
- Check Render logs for any errors

**Data Not Persisting**:
- Verify `DATABASE_URL` is set correctly in Render
- Check Supabase dashboard → Table Editor to see your data

## Managing Your Database

You can view and manage your data directly in Supabase:
1. Go to your Supabase project
2. Click **Table Editor** in the sidebar
3. You'll see all your tables: `schedule`, `assignments`, `notes`, etc.
4. You can view, edit, or delete data directly here

## Free Tier Limits

- **Storage**: 500MB (plenty for a Discord bot)
- **Bandwidth**: 2GB/month
- **API Requests**: Unlimited

Your bot will likely use less than 10MB of storage, so you're well within limits!
