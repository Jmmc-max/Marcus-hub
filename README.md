# Roblox Checker Discord Bot

A safe Discord slash-command bot that checks public Roblox profile information from a Roblox profile link, user ID, or username. It can also mirror each successful check to a Discord webhook.

> This project checks public Roblox user profile data only. It does not check passwords, cookies, private account data, or account validity for credential lists.

## Features

- `/roblox-check target:<link | user id | username>` slash command.
- `/roblox-check-file file:<txt attachment>` slash command for importing up to 750 public targets at once.
- Accepts links like `https://www.roblox.com/users/1/profile`.
- Displays username, display name, user ID, creation date, ban status, description, avatar, and profile link.
- checking username:password of each account 
- Optional webhook posting with `WEBHOOK_URL`.
- Rejects non-Roblox domains; typo domains such as `robiox.com.py` are not accepted.



## Adding your Discord key and ID


### Easier command-based configuration

If editing `.env` is difficult on mobile, run this in your host's Shell/Console:

```bash
npm run configure -- --client-id 153361584328 --public-key YOUR_PUBLIC_KEY --token YOUR_BOT_TOKEN
npm run setup-and-start
```

You can add `--guild-id YOUR_SERVER_ID` if you want faster command registration while testing.


If you already have your Discord bot token (sometimes called the bot key) and application/client ID, add them to a local `.env` file in the project root.

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and replace the placeholder values:

   ```env
   DISCORD_TOKEN=your_real_bot_token_here
   CLIENT_ID=your_real_application_client_id_here
   GUILD_ID=your_discord_server_id_here
   WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_here
   ```

   `DISCORD_TOKEN`, `CLIENT_ID`, and `DISCORD_PUBLIC_KEY` are required. `GUILD_ID` is optional but recommended while testing because guild commands usually update faster than global commands. `WEBHOOK_URL` is optional and only needed if you want the bot to mirror check results to a Discord webhook.

3. Register the slash commands:

   ```bash
   npm run register
   ```

4. Start the bot:

   ```bash
   npm start
   ```

5. Invite the bot to your Discord server from the Discord Developer Portal using the OAuth2 URL Generator. Select these scopes:

   - `bot`
   - `applications.commands`

   The bot needs permission to send messages in any channel where members will use `/roblox-check` or `/roblox-check-file`.

Never paste your real `DISCORD_TOKEN` into Discord chat, GitHub, screenshots, or exported zip files. If it leaks, reset the token in the Discord Developer Portal. See the [security guide](SECURITY.md) if your token or webhook URL is exposed.


## Discord Interactions Endpoint URL

This bot runs as an HTTP Interactions server instead of a gateway bot, so it does not need external npm packages. After deploying, copy your public host URL and set this in the Discord Developer Portal:

```text
https://YOUR_HOST/interactions
```

You also need your application's public key in `DISCORD_PUBLIC_KEY`; Discord uses it so the bot can verify incoming slash-command requests.

## Import file format

Use `/roblox-check-file` with a plain text attachment. Put one public Roblox target per line:

```text
https://www.roblox.com/users/1/profile
Builderman
156
```

Blank lines and lines starting with `#` are ignored. Each import can contain up to 750 targets. The bot reports whether each public profile can be opened/resolved; it never attempts Roblox login checks and cannot report password or 2FA states.

## Setup

- [Discord setup guide](DISCORD_SETUP.md) for adding the `/interactions` URL and inviting the bot.
- [Security guide](SECURITY.md) for what to do if a Discord token or webhook URL is exposed.
- [Mobile setup guide](MOBILE_SETUP.md) for phone-based setup and hosting options.

1. Install Node.js 18.17 or newer.
2. Copy the example environment file and fill in your Discord values:

   ```bash
   cp .env.example .env
   ```

3. Register the slash command:

   ```bash
   npm run register
   ```

4. Start the bot:

   ```bash
   npm start
   ```

   If your mobile host only gives you one Run button, use:

   ```bash
   npm run setup-and-start
   ```

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `DISCORD_TOKEN` | Yes | Discord bot token from the Discord Developer Portal. |
| `CLIENT_ID` | Yes | Discord application client ID. |
| `DISCORD_PUBLIC_KEY` | Yes | Discord application public key used to verify interaction requests. |
| `PORT` | No | HTTP server port. Defaults to `3000`. |
| `GUILD_ID` | No | Discord server ID for fast development command registration. Omit for global commands. |
| `WEBHOOK_URL` | No | Discord webhook URL used to mirror successful checker results. |

## Bot permissions

Invite the bot with the `applications.commands` scope so slash commands work. The bot also needs permission to send messages in channels where users run the command.

## Exporting and running without a `.env` file

If you do not want to create a `.env` file, export the required values in your terminal before running the registration or bot commands.

### macOS, Linux, and most hosting shells

```bash
export DISCORD_TOKEN="your_discord_bot_token"
export CLIENT_ID="your_discord_application_client_id"
export GUILD_ID="your_discord_server_id"
export WEBHOOK_URL="https://discord.com/api/webhooks/..."

npm run register
npm start
```

`GUILD_ID` and `WEBHOOK_URL` are optional. Leave `GUILD_ID` unset for global slash-command registration, and leave `WEBHOOK_URL` unset if you do not want webhook logging.

### Windows PowerShell

```powershell
$env:DISCORD_TOKEN="your_discord_bot_token"
$env:CLIENT_ID="your_discord_application_client_id"
$env:GUILD_ID="your_discord_server_id"
$env:WEBHOOK_URL="https://discord.com/api/webhooks/..."

npm run register
npm start
```

### Exporting the project as a zip

To share or upload the bot files without Git history or installed dependencies, create a zip from the repository root:

```bash
zip -r roblox-checker-bot.zip . -x ".git/*" "node_modules/*" ".env"
```

Do not include your `.env` file or real Discord token in exported archives.
