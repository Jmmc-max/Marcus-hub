# Mobile setup guide

- [Discord setup guide](DISCORD_SETUP.md) for adding the `/interactions` URL and inviting the bot.

You can configure the bot from a phone, but the bot must run somewhere that stays online. The easiest mobile-friendly path is to use a browser-based host such as Replit, Render, Railway, Koyeb, or another Node.js host. Termux can work on Android for testing, but your phone must stay awake and connected.


## Easiest mobile command setup

If editing `.env` on mobile is hard, use the configure command from your host's Shell/Console. Your application/client ID goes into `CLIENT_ID`.

```bash
npm run configure -- --client-id 153361584328 --public-key YOUR_PUBLIC_KEY --token YOUR_BOT_TOKEN
npm run setup-and-start
```

If you also know your Discord server ID, add it so slash commands update faster:

```bash
npm run configure -- --client-id 153361584328 --guild-id YOUR_SERVER_ID --token YOUR_BOT_TOKEN
npm run setup-and-start
```

The configure command creates a local `.env` file and masks secrets in the console output. Do not paste your real bot token in Discord chat or commit it to GitHub.

## Option 1: Browser-based Node.js host (recommended)

1. Open your hosting provider from your mobile browser.
2. Create a new Node.js project or import this GitHub repository.
3. Add environment variables in the host's Secrets/Environment settings:

   | Name | Value |
   | --- | --- |
   | `DISCORD_TOKEN` | Your Discord bot token/key |
   | `CLIENT_ID` | Your Discord application/client ID |
   | `GUILD_ID` | Optional Discord server ID for faster command registration |
   | `WEBHOOK_URL` | Optional Discord webhook URL for check logs |

4. Open the host's shell/console and run:

   ```bash
   npm run register
   npm start
   ```

5. Keep the app running using your host's normal always-on/deploy setting.


## If your mobile host does not show a Node.js run option

Some mobile editors or hosts hide the normal terminal/run controls. Try these options:

1. Look for a button named **Shell**, **Console**, **Terminal**, **Tools**, or **Commands**.
2. If the host asks for a language/template, choose **Node.js**. If there is no Node.js option, choose **Import from GitHub** or **Blank/Bash project**, then use this repository's files.
3. If the host has a custom run command field, set it to:

   ```bash
   npm run setup-and-start
   ```

4. If you can only run commands one at a time, run:

   ```bash
   npm run register
   npm start
   ```

This repository includes a `.replit` file so Replit-style hosts can show a Run button that executes `npm run setup-and-start`.

## Option 2: Android with Termux

1. Install Termux from F-Droid.
2. Open Termux and run:

   ```bash
   pkg update
   pkg install nodejs git
   git clone <your-repository-url>
   cd <your-repository-folder>
   ```

3. Create a `.env` file:

   ```bash
   cp .env.example .env
   nano .env
   ```

4. Fill in your Discord values, save the file, then run:

   ```bash
   npm run register
   npm start
   ```

Termux is best for testing. If Android kills Termux or your phone disconnects, the bot will go offline.


## Discord Interactions Endpoint URL from mobile

After the host starts the bot, copy its public URL and add `/interactions` at the end. Put that full URL into the Discord Developer Portal as the app's Interactions Endpoint URL:

```text
https://YOUR_HOST/interactions
```

If Discord rejects the endpoint, confirm `DISCORD_PUBLIC_KEY` is set correctly and your host is publicly reachable.

## Inviting the bot from mobile

1. Open the Discord Developer Portal in your mobile browser.
2. Select your application.
3. Go to OAuth2 / URL Generator.
4. Select these scopes:
   - `bot`
   - `applications.commands`
5. Copy the generated URL, open it in your browser, and choose your Discord server.

## Mobile checklist

- Do not put your real bot token in GitHub files or Discord messages.
- Use host Secrets/Environment Variables when deploying online.
- Run `npm run register` again after changing slash commands.
- Use `GUILD_ID` while testing so commands update faster.
- Use `/roblox-check` for one profile or `/roblox-check-file` with a `.txt` attachment for batch checks.
