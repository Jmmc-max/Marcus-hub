# Add the bot to Discord

This project runs as a Discord Interactions HTTP server. That means Discord sends slash-command requests to your public `/interactions` URL.

## 1. Put your values into the host

In your hosting service's Secrets/Environment Variables, add:

| Name | Value |
| --- | --- |
| `DISCORD_TOKEN` | Your new/reset bot token |
| `CLIENT_ID` | Your Discord application/client ID |
| `DISCORD_PUBLIC_KEY` | Your Discord application public key |
| `GUILD_ID` | Optional server ID for faster command registration |
| `WEBHOOK_URL` | Optional webhook URL for logs |
| `PORT` | Optional HTTP port for the Interactions server. Defaults to `3000`. |

Do not use a token that has been pasted in chat. Reset it first.

## 2. Start the server

Run this on your host:

```bash
npm run setup-and-start
```

The server prints this reminder when it starts:

```text
Set your Discord Interactions Endpoint URL to: https://YOUR_HOST:3000/interactions
```

## 3. Add the Interactions Endpoint URL in Discord

1. Open the Discord Developer Portal.
2. Select your application.
3. Go to **General Information**.
4. Find **Interactions Endpoint URL**.
5. Paste your public host URL with `/interactions` at the end. If your host exposes a custom port, include it in the URL:

   ```text
   https://YOUR_HOST:3000/interactions
   ```

6. Save changes.

If Discord rejects the URL, check that:

- Your host is running.
- The URL is public and starts with `https://`.
- The URL ends with `/interactions`.
- The URL includes the public port when your host requires one, for example `https://YOUR_HOST:3000/interactions`.
- If your reverse proxy maps public HTTPS port `443` to the app internally, do not include `:3000` in Discord; use `https://YOUR_HOST/interactions`.
- `DISCORD_PUBLIC_KEY` is set correctly.

## 4. Register slash commands

If you used `npm run setup-and-start`, command registration already ran. If you need to register again, run:

```bash
npm run register
```

Using `GUILD_ID` makes commands appear faster in one server. Without `GUILD_ID`, Discord registers commands globally and they may take longer to appear.

## 5. Invite the bot to your server

1. Open the Discord Developer Portal.
2. Select your application.
3. Go to **OAuth2** > **URL Generator**.
4. Select these scopes:
   - `bot`
   - `applications.commands`
5. Select bot permissions needed for your server, at minimum permission to send messages in channels where commands are used.
6. Copy the generated URL and open it.
7. Choose your server and authorize the bot.

After that, try `/roblox-check` in your Discord server.
