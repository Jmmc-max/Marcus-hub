"""Safe discord.py bot for validating username:password line format.

This bot intentionally does not log in to Discord, Roblox, or any other
service with submitted credentials. It only checks whether each supplied line
looks like a `username:password` pair so it can be used for input hygiene
without enabling credential stuffing or account takeover.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

MISSING_DEPENDENCIES = [
    package
    for package, module in (("discord.py", "discord"),)
    if importlib.util.find_spec(module) is None
]
if MISSING_DEPENDENCIES:
    missing = ", ".join(MISSING_DEPENDENCIES)
    raise RuntimeError(
        f"Missing Python dependency/dependencies: {missing}. "
        "Install them with: python -m pip install -r requirements.txt"
    )

import discord
from discord import app_commands

from credential_format import (
    MAX_FILE_LINES,
    summarize_results,
    validate_username_password_text,
)
from env_loader import load_env_file
from key_store import create_lifetime_key, user_has_lifetime_key

load_env_file()

MAX_ATTACHMENT_BYTES = 512_000
OWNER_IDS = {
    int(owner_id.strip())
    for owner_id in os.getenv("OWNER_IDS", "").split(",")
    if owner_id.strip().isdigit()
}
KEY_STORE_PATH = Path(os.getenv("KEY_STORE_PATH", "data/lifetime_keys.json"))


class SafeCredentialFormatBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        guild_id = os.getenv("GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()


bot = SafeCredentialFormatBot()


def is_owner(user_id: int) -> bool:
    """Return whether the user can create lifetime keys."""
    return user_id in OWNER_IDS


def has_bot_access(user_id: int) -> bool:
    """Return whether the user can run checker commands."""
    return is_owner(user_id) or user_has_lifetime_key(user_id, KEY_STORE_PATH)


async def require_bot_access(interaction: discord.Interaction) -> bool:
    """Send an access warning when the user has no lifetime key."""
    if has_bot_access(interaction.user.id):
        return True

    await interaction.response.send_message(
        "You need a lifetime key before using this bot. Ask the bot owner to run "
        "`/create-lifetime-key` for your Discord account.",
        ephemeral=True,
    )
    return False


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id if bot.user else 'unknown'})")


@bot.tree.command(
    name="create-lifetime-key",
    description="Owner-only: create a lifetime key for another Discord user.",
)
@app_commands.describe(
    user="Discord user who should receive lifetime access.",
    note="Optional private note stored with the key.",
)
async def make_lifetime_key(
    interaction: discord.Interaction,
    user: discord.User,
    note: str = "",
) -> None:
    if not is_owner(interaction.user.id):
        await interaction.response.send_message(
            "Only configured bot owners can create lifetime keys. Add your Discord user ID to `OWNER_IDS` in `.env`.",
            ephemeral=True,
        )
        return

    lifetime_key = create_lifetime_key(
        user_id=user.id,
        created_by=interaction.user.id,
        note=note,
        path=KEY_STORE_PATH,
    )
    await interaction.response.send_message(
        f"Created lifetime key for {user.mention}: `{lifetime_key.key}`",
        ephemeral=True,
    )


async def send_format_check_response(
    interaction: discord.Interaction,
    entries: str,
    max_lines: int | None = None,
) -> None:
    """Validate entries and send a safe checker response."""
    if not await require_bot_access(interaction):
        return

    results = validate_username_password_text(entries, max_lines=max_lines)
    if not results:
        await interaction.response.send_message("No entries were provided.", ephemeral=True)
        return

    await interaction.response.send_message(summarize_results(results)[:2000], ephemeral=True)


@bot.tree.command(
    name="username-password-checker",
    description="Safely check username:password text format without logging in anywhere.",
)
@app_commands.describe(entries="One or more username:password lines, up to 25 lines.")
async def username_password_checker(interaction: discord.Interaction, entries: str) -> None:
    await send_format_check_response(interaction, entries)


@bot.tree.command(
    name="check-format",
    description="Alias: safely validate username:password text format.",
)
@app_commands.describe(entries="One or more username:password lines, up to 25 lines.")
async def check_format(interaction: discord.Interaction, entries: str) -> None:
    await send_format_check_response(interaction, entries)


@bot.tree.command(
    name="username-password-checker-file",
    description="Safely check a username:password text file without logging in anywhere.",
)
@app_commands.describe(file="Plain text file with one username:password entry per line.")
async def username_password_checker_file(interaction: discord.Interaction, file: discord.Attachment) -> None:
    if not await require_bot_access(interaction):
        return

    if file.size > MAX_ATTACHMENT_BYTES:
        await interaction.response.send_message(
            f"File is too large. Maximum size is {MAX_ATTACHMENT_BYTES} bytes.",
            ephemeral=True,
        )
        return

    content_type = file.content_type or ""
    if content_type and "text/" not in content_type and "octet-stream" not in content_type:
        await interaction.response.send_message(
            "Please upload a plain text file.",
            ephemeral=True,
        )
        return

    data = await file.read()
    text = data.decode("utf-8", errors="replace")
    await send_format_check_response(interaction, text, max_lines=MAX_FILE_LINES)


@bot.tree.command(
    name="check-file",
    description="Alias: safely validate a username:password text file.",
)
@app_commands.describe(file="Plain text file with one username:password entry per line.")
async def check_file(interaction: discord.Interaction, file: discord.Attachment) -> None:
    await username_password_checker_file(interaction, file)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable.")

    bot.run(token)


if __name__ == "__main__":
    main()
