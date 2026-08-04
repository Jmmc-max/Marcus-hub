# Deploy the standalone Discord checker bot

This guide is for running `discord_bot_checker.py` on a new server. The checker bot uses `discord.py`, slash commands, and a local JSON approval store.

> Safety note: this bot only validates `username:password` text format. It does not log in with submitted credentials, approve real account passwords, or check whether any account is valid.

## Files to copy to a new server

Copy these files and folders from the repository:

| Path | Why it is needed |
| --- | --- |
| `discord_bot_checker.py` | Main standalone checker bot entrypoint. |
| `credential_format.py` | Safe `username:password` format validation helpers. |
| `env_loader.py` | Loads local `.env` values without adding another dependency. |
| `key_store.py` | Stores approved Discord users in a local JSON file. |
| `requirements.txt` | Python dependencies for the bot. |
| `.env.checker.example` | Template for the server's private `.env` file. |
| `.gitignore` | Keeps `.env`, logs, caches, and local key data out of Git. |

Keep the `data/` directory persistent if your host uses ephemeral storage, because `KEY_STORE_PATH` defaults to `data/lifetime_keys.json`.

## 1. Create the Discord application and bot

1. Open the Discord Developer Portal.
2. Create or select an application.
3. Open **Bot** and create/reset the bot token.
4. Enable the bot for your server with OAuth2 scopes:
   - `bot`
   - `applications.commands`
5. Invite the bot to your server.

## 2. Install on a Linux server

Run these commands on the server:

```bash
git clone YOUR_REPOSITORY_URL Marcus-hub
cd Marcus-hub
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.checker.example .env
```

Edit `.env` and set real values:

```env
DISCORD_TOKEN=your_real_bot_token
GUILD_ID=your_discord_server_id
OWNER_IDS=your_discord_user_id
KEY_STORE_PATH=data/lifetime_keys.json
```

Then start the bot:

```bash
python discord_bot_checker.py
```

## 3. Run it as a systemd service

Create `/etc/systemd/system/discord-checker-bot.service`:

```ini
[Unit]
Description=Standalone Discord username-password format checker bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/Marcus-hub
EnvironmentFile=/opt/Marcus-hub/.env
ExecStart=/opt/Marcus-hub/.venv/bin/python /opt/Marcus-hub/discord_bot_checker.py
Restart=always
RestartSec=10
User=discordbot
Group=discordbot

[Install]
WantedBy=multi-user.target
```

Adjust `WorkingDirectory`, `EnvironmentFile`, `ExecStart`, `User`, and `Group` for your server path and Linux user. Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now discord-checker-bot
sudo systemctl status discord-checker-bot
```

View logs with:

```bash
journalctl -u discord-checker-bot -f
```

## 4. First Discord commands

1. Restart the bot after editing `.env`.
2. In Discord, have an owner run `/approve-checker-user user:@someone`.
3. Approved users can run `/check-username-password` or `/check-username-password-file`.

## Troubleshooting

- If slash commands do not appear, set `GUILD_ID` to your server ID and restart the bot.
- If startup says `Missing DISCORD_TOKEN environment variable`, check that `.env` exists in the bot working directory.
- If approval disappears after redeploying, make sure `data/lifetime_keys.json` is on persistent storage.
- If Discord says the bot is missing access, regenerate the invite URL with the `applications.commands` scope.
