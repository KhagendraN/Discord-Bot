# Deploying Class Assistant Bot on Render

This guide explains how to deploy your Discord bot to [Render](https://render.com) as a **Web Service**.

## Why Web Service?
We use a "Web Service" instead of a "Background Worker" because Render's free tier spins down inactive web services but allows them to be kept alive if they receive HTTP traffic. We have included a `keep_alive.py` script that runs a small Flask server alongside your bot to satisfy this requirement and allow for health checks.

## Prerequisites
1.  A [GitHub](https://github.com) account with this code pushed to a repository.
2.  A [Render](https://render.com) account.

## Option 1: Manual Deployment (Recommended)

1.  **Create a New Service**
    *   Log in to the Render Dashboard.
    *   Click **New +** and select **Web Service**.

2.  **Connect Repository**
    *   Connect your GitHub account if you haven't already.
    *   Search for your repository (`class-assistant-bot`) and click **Connect**.

3.  **Configure Service**
    *   **Name**: `class-assistant-bot` (or any name you prefer).
    *   **Region**: Choose the one closest to you (e.g., Singapore, Frankfurt).
    *   **Branch**: `main` (or your working branch).
    *   **Root Directory**: Leave blank (defaults to repo root).
    *   **Runtime**: **Docker** (Important: Do not select Python).
    *   **Instance Type**: Free (or Starter).

4.  **Environment Variables**
    *   Scroll down to the **Environment Variables** section and add the following keys. You can find these values in your local `.env` file or `configuration.config`.

    | Key | Value Description |
    | :--- | :--- |
    | `DATABASE_URL` | **Required**: Your PostgreSQL connection string from Supabase. See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for setup instructions. |
    | `DISCORD_TOKEN` | Your Discord Bot Token. |
    | `MISTRAL_API_KEY` | Your Mistral AI API Key. |
    | `CR_USER_ID` | (Optional) The Discord User ID of the Class Representative. |
    | `CR_ROLE_NAME` | (Optional) The role name for CR permissions (e.g., "CR"). |
    | `ANNOUNCEMENT_CHANNEL_ID` | (Optional) Channel ID for daily reminders. |

    > **Important**: You must set up a PostgreSQL database first. Follow the [Supabase Setup Guide](SUPABASE_SETUP.md) to create a free database and get your `DATABASE_URL`.

5.  **Deploy**
    *   Click **Create Web Service**.
    *   Render will start building your Docker image. This may take a few minutes.
    *   Once built, it will deploy the service. You should see "Service is live" and your bot should come online in Discord.

## Option 2: Blueprint Deployment (Advanced)

If you prefer infrastructure-as-code, you can use the `render.yaml` file included in the repository.

1.  In Render Dashboard, click **New +** and select **Blueprint**.
2.  Connect your repository.
3.  Render will detect `render.yaml` and prompt you for the environment variables defined in it.
4.  Fill in the values and click **Apply**.

## Troubleshooting

*   **Build Failed**: Check the "Logs" tab in Render. Ensure `requirements.txt` has all dependencies.
*   **Bot Offline**: Check the "Logs" tab. Look for Python errors or "Improper token" messages. Ensure `DISCORD_TOKEN` is correct.
*   **Health Check Failed**: Ensure `src/keep_alive.py` is running. The Dockerfile is configured to run `./scripts/start.sh`, which starts this script.
*   **Database Error**: The bot automatically uses `/data/class_data.db` on Render (which is writable). Locally, it uses the project root.

## Important Notes

### Database Persistence
*   **PostgreSQL (Recommended)**: The bot uses PostgreSQL via the `DATABASE_URL` environment variable for permanent data storage.
*   **Free Supabase**: 500MB database that never sleeps. Follow [SUPABASE_SETUP.md](SUPABASE_SETUP.md) to set it up.
*   **SQLite Fallback**: If `DATABASE_URL` is not set, the bot falls back to SQLite (useful for local development).
*   Your data (schedules, assignments, notes, materials) will persist permanently with PostgreSQL.
