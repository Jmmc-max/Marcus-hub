import key_store


def test_create_lifetime_key_stores_user_access(tmp_path):
    path = tmp_path / "keys.json"
    lifetime_key = key_store.create_lifetime_key(
        user_id=123,
        created_by=456,
        note="tester",
        path=path,
    )

    assert lifetime_key.key.startswith("LIFE-")
    assert key_store.user_has_lifetime_key(123, path) is True
    assert key_store.user_has_lifetime_key(999, path) is False


def test_load_lifetime_keys_returns_empty_when_missing(tmp_path):
    assert key_store.load_lifetime_keys(tmp_path / "missing.json") == {}
