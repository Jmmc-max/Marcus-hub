import credential_format


def test_valid_username_password_line():
    result = credential_format.validate_username_password_line(
        "alice:correct horse battery staple",
        1,
    )
    assert result.ok is True
    assert result.message == "valid format"


def test_missing_separator_is_rejected():
    result = credential_format.validate_username_password_line("alice", 1)
    assert result.ok is False
    assert result.message == "missing ':' separator"


def test_limits_batch_to_max_lines():
    text = "\n".join(
        f"user{i}:pass{i}" for i in range(credential_format.MAX_LINES + 5)
    )
    results = credential_format.validate_username_password_text(text)
    assert len(results) == credential_format.MAX_LINES


def test_file_line_limit_can_be_requested():
    text = "\n".join(
        f"user{i}:pass{i}" for i in range(credential_format.MAX_FILE_LINES + 5)
    )
    results = credential_format.validate_username_password_text(
        text,
        max_lines=credential_format.MAX_FILE_LINES,
    )
    assert len(results) == credential_format.MAX_FILE_LINES


def test_summary_counts_valid_and_invalid_lines():
    results = credential_format.validate_username_password_text("alice:pass\nbob")
    summary = credential_format.summarize_results(results)
    assert "Valid format: 1/2" in summary
    assert "Invalid format: 1/2" in summary
