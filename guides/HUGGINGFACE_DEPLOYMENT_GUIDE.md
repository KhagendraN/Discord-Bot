# Deploying Class Assistant Bot on Hugging Face Spaces

This guide explains how to deploy your Discord bot to [Hugging Face Spaces](https://huggingface.co/spaces) using Docker.

## Why Hugging Face Spaces?
Hugging Face Spaces offers a simple way to host machine learning demos and apps. By using the Docker SDK, we can deploy our custom Discord bot environment. The free tier is generous and suitable for many bot applications.

## Prerequisites
1.  A [Hugging Face](https://huggingface.co) account.
2.  A [GitHub](https://github.com) account with this code pushed to a repository (optional, but recommended for syncing).

## Deployment Steps

### 1. Create a New Space
1.  Log in to Hugging Face.
2.  Click on your profile picture and select **New Space**.
3.  **Space Name**: `class-assistant-bot` (or any name you prefer).
4.  **License**: MIT (or your choice).
5.  **SDK**: Select **Docker**.
6.  **Space Hardware**: **CPU Basic (Free)** is usually sufficient.
7.  **Visibility**: Public or Private (Private is recommended if you want to hide your source code/logs, but Public is fine if you don't mind).

### 2. Configure the Space
After creating the Space, you'll see a "Building" status. It might fail initially if environment variables aren't set.

1.  Go to the **Settings** tab of your Space.
2.  Scroll down to the **Variables and secrets** section.
3.  Click **New secret** to add your sensitive environment variables.

### 3. Set Environment Variables (Secrets)
Add the following secrets. You can find these values in your local `.env` file.

| Key | Value Description |
| :--- | :--- |
| `DATABASE_URL` | **Required**: Your PostgreSQL connection string from Supabase. See [SUPABASE_SETUP.md](SUPABASE_SETUP.md) for setup instructions. |
| `DISCORD_TOKEN` | Your Discord Bot Token. |
| `MISTRAL_API_KEY` | Your Mistral AI API Key. |
| `CR_USER_ID` | (Optional) The Discord User ID of the Class Representative. |
| `CR_ROLE_NAME` | (Optional) The role name for CR permissions (e.g., "CR"). |
| `ANNOUNCEMENT_CHANNEL_ID` | (Optional) Channel ID for daily reminders. |

> **Note**: Hugging Face Spaces exposes port `7860` by default. The `Dockerfile` in this repo is configured to expose this port and the bot's keep-alive server listens on it.

### 4. Sync with GitHub (Optional but Recommended)
If you want to push code from your local machine/GitHub to the Space:
1.  In the Space **Settings**, look for "Git" or "Repository".
2.  You can add your GitHub repository as a remote or use GitHub Actions to push to the Space.
3.  Alternatively, you can manually upload files via the "Files" tab, but using Git is better.

### 5. Verify Deployment
1.  Go to the **App** tab.
2.  You should see "Running" status.
3.  The app preview might show a JSON response `{"status": "ok", "service": "class-assistant-bot"}`. This means the keep-alive server is running.
4.  Check your Discord server; the bot should be online!

## Troubleshooting

*   **Build Failed**: Check the "Logs" tab. Ensure `requirements.txt` is correct and the Dockerfile build process finishes without errors.
*   **Runtime Error**: If the build succeeds but the app crashes, check the "Logs".
*   **Port Issues**: If the app is "Running" but the health check fails or the bot doesn't stay online, ensure the `PORT` environment variable is effectively being used (defaults to 7860 in Dockerfile).
*   **Database**: Ensure `DATABASE_URL` is correct. The bot relies on Supabase for persistence. Local SQLite files in the Space will be lost when the Space restarts.

## Important Notes

### Persistence
*   **PostgreSQL (Supabase)**: Highly recommended. Data is stored externally and persists across restarts.
*   **Local Storage**: Hugging Face Spaces are ephemeral. Any files written to the disk (like a local SQLite DB) will be lost when the Space restarts or rebuilds. **Always use Supabase for production.**
