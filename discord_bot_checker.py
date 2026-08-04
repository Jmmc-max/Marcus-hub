"""Standalone safe discord.py bot for username:password format checks.

This bot is intentionally limited to format validation. It never sends submitted
usernames or passwords to Discord, Roblox, or any other service, and it never
attempts to approve, reject, or authenticate credentials.
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


class DiscordCheckerBot(discord.Client):
    """Discord client that registers safe checker slash commands."""

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
            return

        await self.tree.sync()


bot = DiscordCheckerBot()


def is_owner(user_id: int) -> bool:
    """Return whether the user can approve Discord users for this bot."""
    return user_id in OWNER_IDS


def is_approved_user(user_id: int) -> bool:
    """Return whether the user is approved to run checker commands."""
    return is_owner(user_id) or user_has_lifetime_key(user_id, KEY_STORE_PATH)


async def require_approved_user(interaction: discord.Interaction) -> bool:
    """Block checker commands until an owner approves the Discord user."""
    if is_approved_user(interaction.user.id):
        return True

    await interaction.response.send_message(
        "You are not approved to use this checker yet. Ask a bot owner to run "
        "`/approve-checker-user` for your Discord account.",
        ephemeral=True,
    )
    return False


@bot.event
async def on_ready() -> None:
    print(f"Logged in as {bot.user} (ID: {bot.user.id if bot.user else 'unknown'})")


@bot.tree.command(
    name="approve-checker-user",
    description="Owner-only: approve a Discord user to run safe checker commands.",
)
@app_commands.describe(
    user="Discord user who should be allowed to use checker commands.",
    note="Optional private note stored with the approval key.",
)
async def approve_checker_user(
    interaction: discord.Interaction,
    user: discord.User,
    note: str = "",
) -> None:
    """Approve a Discord user without approving any submitted credentials."""
    if not is_owner(interaction.user.id):
        await interaction.response.send_message(
            "Only configured bot owners can approve checker users. Add your Discord user ID to `OWNER_IDS`.",
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
        f"Approved {user.mention} for checker access. Approval key: `{lifetime_key.key}`",
        ephemeral=True,
    )


async def send_checker_response(
    interaction: discord.Interaction,
    entries: str,
    max_lines: int | None = None,
) -> None:
    """Validate username:password text format and send an ephemeral response."""
    if not await require_approved_user(interaction):
        return

    results = validate_username_password_text(entries, max_lines=max_lines)
    if not results:
        await interaction.response.send_message("No entries were provided.", ephemeral=True)
        return

    await interaction.response.send_message(summarize_results(results)[:2000], ephemeral=True)


@bot.tree.command(
    name="check-username-password",
    description="Check username:password format without authenticating credentials.",
)
@app_commands.describe(entries="One or more username:password lines to format-check.")
async def check_username_password(interaction: discord.Interaction, entries: str) -> None:
    await send_checker_response(interaction, entries)


@bot.tree.command(
    name="check-username-password-file",
    description="Check a plain-text username:password file without logging in anywhere.",
)
@app_commands.describe(file="Plain text file with one username:password entry per line.")
async def check_username_password_file(interaction: discord.Interaction, file: discord.Attachment) -> None:
    if not await require_approved_user(interaction):
        return

    if file.size > MAX_ATTACHMENT_BYTES:
        await interaction.response.send_message(
            f"File is too large. Maximum size is {MAX_ATTACHMENT_BYTES} bytes.",
            ephemeral=True,
        )
        return

    content_type = file.content_type or ""
    if content_type and "text/" not in content_type and "octet-stream" not in content_type:
        await interaction.response.send_message("Please upload a plain text file.", ephemeral=True)
        return

    data = await file.read()
    text = data.decode("utf-8", errors="replace")
    await send_checker_response(interaction, text, max_lines=MAX_FILE_LINES)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable.")

    bot.run(token)


if __name__ == "__main__":
    main()
