import os

from env_loader import load_env_file


def test_load_env_file_reads_key_values_without_overriding(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("TOKEN=from-file\nEXISTING=from-file\n# ignored\n", encoding="utf-8")
    monkeypatch.setenv("EXISTING", "already-set")

    load_env_file(env_path)

    assert os.environ["TOKEN"] == "from-file"
    assert os.environ["EXISTING"] == "already-set"
