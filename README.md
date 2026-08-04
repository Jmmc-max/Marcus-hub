# Discord.py Username:Password Format Bot

A safe `discord.py` slash-command bot for checking whether pasted text or uploaded plain-text files use the `username:password` format.

> This project does not check passwords, tokens, cookies, private account data, or whether any account credentials are valid. It only checks text format.

## Features

- `/create-lifetime-key user:<member>` owner-only command for granting lifetime access to another Discord user.
- `/username-password-checker entries:<text>` command for checking pasted `username:password` lines.
- `/username-password-checker-file file:<txt attachment>` command for faster checking of plain-text files with up to 1,000 lines.
- Local JSON key storage with configurable `KEY_STORE_PATH`.
- Ephemeral Discord responses so checker output is only shown to the command user.

## Setup

1. Install Python 3.11 or newer.
2. Install the Python dependency:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Copy the example environment file, then edit `.env` with your Discord values:

   ```bash
   cp .env.example .env
   ```

   The `.env.example` file contains:

   ```env
   DISCORD_TOKEN=your_real_bot_token_here
   GUILD_ID=your_discord_server_id_here
   OWNER_IDS=your_discord_user_id_here
   KEY_STORE_PATH=data/lifetime_keys.json
   ```

   The bot loads `.env` automatically. `DISCORD_TOKEN` is required. `GUILD_ID` is optional, but it makes slash-command syncing faster while testing. `OWNER_IDS` is a comma-separated list of Discord user IDs allowed to run `/create-lifetime-key`. `KEY_STORE_PATH` is optional and defaults to `data/lifetime_keys.json`.

4. Start the main bot:

   ```bash
   python bot.py
   ```

   Or start the standalone checker bot file with the `/approve-checker-user`, `/check-username-password`, and `/check-username-password-file` commands:

   ```bash
   python discord_bot_checker.py
   ```

5. In Discord, have an owner run `/create-lifetime-key user:@someone` to give a user lifetime access. Approved users can then run `/username-password-checker` or upload a text file to `/username-password-checker-file`.

## Standalone checker deployment

For a new server, copy `.env.checker.example` to `.env`, install `requirements.txt`, and run `python discord_bot_checker.py`. See `CHECKER_DEPLOY.md` for the full server checklist, systemd service example, and required files.

## File format

Use one `username:password` entry per line:

```text
example_user:example_password
another_user:another_password
```

Blank lines, missing separators, empty usernames, empty passwords, and overly long fields are reported as invalid format. Only use test data or credentials you own, and never paste real passwords into shared channels.

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | Yes | Discord bot token from the Discord Developer Portal. |
| `OWNER_IDS` | Yes for key creation | Comma-separated Discord user IDs allowed to create lifetime keys. |
| `GUILD_ID` | No | Discord server ID for fast development command registration. Omit for global command sync. |
| `KEY_STORE_PATH` | No | Local JSON file used to store lifetime keys. Defaults to `data/lifetime_keys.json`. |

## If startup fails

- If you see `Missing Python dependency/dependencies: discord.py`, run `python -m pip install -r requirements.txt`.
- If you see `Missing DISCORD_TOKEN environment variable`, copy `.env.example` to `.env` and add your real Discord bot token.
- If `/create-lifetime-key` says only owners can create keys, add your Discord user ID to `OWNER_IDS` in `.env` and restart the bot.

## Security notes

- Never commit `.env` or share your real Discord bot token.
- `data/lifetime_keys.json` is ignored by Git because it contains access keys.
- This bot intentionally never logs in with submitted `username:password` entries and cannot report whether credentials are correct.
