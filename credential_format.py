"""Helpers for safe username:password format validation.

These functions never authenticate submitted credentials against any service.
"""

from __future__ import annotations

from dataclasses import dataclass

MAX_LINES = 25
MAX_FILE_LINES = 1_000
MAX_FIELD_LENGTH = 128
MAX_RESULT_LINES = 40


@dataclass(frozen=True)
class CredentialFormatResult:
    line_number: int
    ok: bool
    message: str


def validate_username_password_line(line: str, line_number: int) -> CredentialFormatResult:
    """Validate one username:password line without authenticating it anywhere."""
    if not line.strip():
        return CredentialFormatResult(line_number, False, "blank line")

    if ":" not in line:
        return CredentialFormatResult(line_number, False, "missing ':' separator")

    username, password = line.split(":", 1)
    username = username.strip()
    password = password.strip()

    if not username:
        return CredentialFormatResult(line_number, False, "missing username")

    if not password:
        return CredentialFormatResult(line_number, False, "missing password")

    if len(username) > MAX_FIELD_LENGTH:
        return CredentialFormatResult(line_number, False, "username is too long")

    if len(password) > MAX_FIELD_LENGTH:
        return CredentialFormatResult(line_number, False, "password is too long")

    return CredentialFormatResult(line_number, True, "valid format")


def validate_username_password_text(
    text: str,
    max_lines: int = MAX_LINES,
) -> list[CredentialFormatResult]:
    """Validate up to max_lines username:password lines."""
    lines = text.splitlines()[:max_lines]
    return [validate_username_password_line(line, index + 1) for index, line in enumerate(lines)]


def summarize_results(results: list[CredentialFormatResult]) -> str:
    """Build a compact Discord message for validation results."""
    valid_count = sum(result.ok for result in results)
    invalid_count = len(results) - valid_count
    shown_results = results[:MAX_RESULT_LINES]
    lines = [
        f"{'✅' if result.ok else '❌'} Line {result.line_number}: {result.message}"
        for result in shown_results
    ]

    if len(results) > len(shown_results):
        lines.append(f"…and {len(results) - len(shown_results)} more line(s).")

    return (
        "I can validate the format of `username:password` entries, but I will not "
        "authenticate credentials or check whether accounts are valid.\n\n"
        f"Valid format: {valid_count}/{len(results)}\n"
        f"Invalid format: {invalid_count}/{len(results)}\n"
        + "\n".join(lines)
    )
