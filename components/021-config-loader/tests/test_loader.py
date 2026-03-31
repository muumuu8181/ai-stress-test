import os
import time
from pathlib import Path
import pytest
from config_loader import ConfigLoader, Config, Validator, SchemaField

@pytest.fixture
def config_dir(tmp_path):
    d = tmp_path / "config"
    d.mkdir()
    return d

def test_loader_merging(config_dir):
    json_file = config_dir / "base.json"
    json_file.write_text('{"app": {"name": "test", "port": 8080}}')

    toml_file = config_dir / "overrides.toml"
    toml_file.write_text('[app]\nport = 9000\ndebug = true')

    loader = ConfigLoader(base_path=config_dir)
    config = loader.load(config_files=["base.json", "overrides.toml"])

    assert config.app.name == "test"
    assert config.app.port == 9000
    assert config.app.debug == True

def test_loader_profile_precedence(config_dir):
    # Two-pass loading check: profile file should override all base files.
    # a.json (env=prod)
    # a.dev.json (env=dev)
    # b.json (env=prod_again)
    # If it was one-pass, it would be a.json -> a.dev.json -> b.json, and result env=prod_again.
    # If it is two-pass, it is a.json -> b.json -> a.dev.json, and result env=dev.

    a_file = config_dir / "a.json"
    a_file.write_text('{"env": "prod"}')

    b_file = config_dir / "b.json"
    b_file.write_text('{"env": "prod_again"}')

    a_dev_file = config_dir / "a.dev.json"
    a_dev_file.write_text('{"env": "dev"}')

    loader = ConfigLoader(base_path=config_dir, profile="dev")
    config = loader.load(config_files=["a.json", "b.json"])

    assert config.env == "dev"

def test_loader_env_profile(config_dir):
    env_file = config_dir / ".env"
    env_file.write_text("FOO=bar")

    env_dev_file = config_dir / ".env.dev"
    env_dev_file.write_text("FOO=baz")

    loader = ConfigLoader(base_path=config_dir, profile="dev")
    config = loader.load(config_files=[".env"])

    assert config.FOO == "baz"

def test_loader_env_vars(config_dir):
    os.environ["APP_DATABASE__HOST"] = "db.host"
    os.environ["APP_DATABASE__PORT"] = "5432"

    loader = ConfigLoader(env_prefix="APP_")
    config = loader.load()

    assert config.database.host == "db.host"
    assert config.database.port == "5432"

    # Cleanup
    del os.environ["APP_DATABASE__HOST"]
    del os.environ["APP_DATABASE__PORT"]

def test_loader_env_vars_overlap(config_dir):
    os.environ["APP_DATABASE"] = "db.host"
    os.environ["APP_DATABASE__PORT"] = "5432"

    loader = ConfigLoader(env_prefix="APP_")
    config = loader.load()

    # Overlap handled by preferring the nested one.
    assert isinstance(config.database.to_dict(), dict)
    assert config.database.port == "5432"

    # Cleanup
    del os.environ["APP_DATABASE"]
    del os.environ["APP_DATABASE__PORT"]

def test_loader_cli_args(config_dir):
    loader = ConfigLoader()
    config = loader.load(cli_args=["--app.port=3000", "--debug"])

    assert config.app.port == "3000"
    assert config.debug == "true"

def test_loader_full_hierarchy(config_dir):
    # Default
    default = {"a": 1, "b": 1, "c": 1, "d": 1}

    # File
    f = config_dir / "config.json"
    f.write_text('{"b": 2, "c": 2, "d": 2}')

    # Env
    os.environ["APP_C"] = "3"
    os.environ["APP_D"] = "3"

    # CLI
    cli_args = ["--d=4"]

    loader = ConfigLoader(base_path=config_dir, env_prefix="APP_")
    config = loader.load(default_config=default, config_files=["config.json"], cli_args=cli_args)

    assert config.a == 1
    assert config.b == 2
    assert config.c == "3"
    assert config.d == "4"

    # Cleanup
    del os.environ["APP_C"]
    del os.environ["APP_D"]

def test_hot_reloading_cli_persistence(config_dir):
    f = config_dir / "config.json"
    f.write_text('{"val": 1}')

    loader = ConfigLoader(base_path=config_dir)
    # CLI override should persist even after file changes
    config = loader.load(config_files=["config.json"], cli_args=["--val=999"])
    assert config.val == "999"

    reloaded_vals = []
    def on_reload(new_cfg):
        reloaded_vals.append(new_cfg.val)

    loader.on_reload(on_reload)
    loader.watch(interval=0.1)

    try:
        # Change file
        time.sleep(0.2)
        f.write_text('{"val": 2}')

        # Wait for reload
        max_wait = 20
        while not reloaded_vals and max_wait > 0:
            time.sleep(0.1)
            max_wait -= 1

        # Even after reload, CLI arg "999" should persist.
        assert "999" in reloaded_vals
    finally:
        loader.stop_watching()

def test_diff(config_dir):
    f = config_dir / "config.json"
    f.write_text('{"val": 1, "other": "x"}')

    loader = ConfigLoader(base_path=config_dir)
    config = loader.load(config_files=["config.json"], cli_args=["--val=2"])

    # Current is val=2 (from CLI), File is val=1
    d = config.diff()
    assert d["val"]["current"] == "2"
    assert d["val"]["file"] == 1
    assert d["val"]["status"] == "modified"
    assert "other" not in d

def test_edge_cases(config_dir):
    loader = ConfigLoader(base_path=config_dir)

    # Non-existent file
    config = loader.load(config_files=["missing.json"])
    assert config.to_dict() == {}

    # Empty file
    f = config_dir / "empty.json"
    f.write_text("")
    config = loader.load(config_files=["empty.json"])
    assert config.to_dict() == {}

    # Malformed file
    f = config_dir / "bad.json"
    f.write_text('{"bad": ')
    with pytest.raises(Exception):
        loader.load(config_files=["bad.json"])

def test_default_config_immutability():
    # Pass a dict with nested dict. Ensure it's not mutated.
    default = {"database": {"host": "localhost"}}
    loader = ConfigLoader()

    # Merge something into database
    config = loader.load(default_config=default, cli_args=["--database.port=5432"])

    assert config.database.port == "5432"
    assert "port" not in default["database"] # Should remain "localhost" only
