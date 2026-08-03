# Security

## If a Discord bot token is exposed

If you paste a real `DISCORD_TOKEN` into chat, GitHub, a screenshot, or any public place, treat it as compromised immediately.

1. Open the Discord Developer Portal.
2. Select your application.
3. Open the bot settings.
4. Reset/regenerate the bot token.
5. Replace the old token in your host's Secrets/Environment Variables or local `.env` file.
6. Restart the bot.

Never commit `.env` or paste your real bot token into support chats. This repository ignores `.env` by default so local secrets do not get committed.

## Values that are safe to share

- `CLIENT_ID` is generally safe to share.
- `DISCORD_PUBLIC_KEY` is generally safe to share.

## Values that must stay private

- `DISCORD_TOKEN`
- Webhook URLs, including `WEBHOOK_URL`
