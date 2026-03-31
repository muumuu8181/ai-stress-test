import os
import sys
import copy
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

from .parsers.json_parser import parse_json
from .parsers.toml_parser import parse_toml
from .parsers.ini_parser import parse_ini
from .parsers.env_parser import parse_env
from .parsers.yaml_parser import parse_yaml_subset
from .schema import Validator
from .watcher import ConfigWatcher

class ConfigLoader:
    """
    Core loader for multi-format configuration files.
    Supports merging from defaults, files, environment variables, and CLI arguments.
    """
    def __init__(
        self,
        base_path: Union[str, Path] = ".",
        env_prefix: str = "APP_",
        schema: Optional[Validator] = None,
        profile: Optional[str] = None
    ):
        """
        Initializes the ConfigLoader.

        Args:
            base_path (Union[str, Path]): Base directory for configuration files.
            env_prefix (str): Prefix for environment variables.
            schema (Optional[Validator]): Optional schema for validation.
            profile (Optional[str]): Configuration profile (e.g., 'dev', 'prod').
        """
        self.base_path = Path(base_path)
        self.env_prefix = env_prefix
        self.schema = schema
        self.profile = profile or os.environ.get(f"{env_prefix}PROFILE", "dev")
        self.config_files: List[Path] = []
        self._raw_config: Dict[str, Any] = {}
        self._last_loaded_files: List[str] = []
        self._default_config: Dict[str, Any] = {}
        self._last_cli_args: Optional[List[str]] = None
        self._watcher: Optional[ConfigWatcher] = None
        self._on_reload_callbacks: List[Callable[['Config'], None]] = []

    def _merge_dicts(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merges two dictionaries."""
        for key, value in dict2.items():
            if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                self._merge_dicts(dict1[key], value)
            else:
                dict1[key] = value
        return dict1

    def _get_parser(self, file_path: Path):
        """Returns the appropriate parser for a given file path based on its extension or name."""
        ext = file_path.suffix.lower()
        name = file_path.name

        if ext == ".json":
            return parse_json
        elif ext == ".toml":
            return parse_toml
        elif ext == ".ini":
            return parse_ini
        elif ext in (".yaml", ".yml"):
            return parse_yaml_subset
        elif name == ".env" or name.startswith(".env."):
            return parse_env
        else:
            raise ValueError(f"Unsupported file format: {name}")

    def load_file(self, file_path: Path) -> Dict[str, Any]:
        """Loads and parses a single configuration file."""
        if not file_path.exists():
            return {}

        parser = self._get_parser(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return parser(content)
        except Exception as e:
            if not file_path.stat().st_size:
                return {}
            raise e

    def load_environment(self) -> Dict[str, Any]:
        """Loads configuration from environment variables based on the env_prefix."""
        env_config = {}
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                config_key = key[len(self.env_prefix):].lower()
                parts = config_key.split("__")

                current = env_config
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    elif not isinstance(current[part], dict):
                        # Handle overlap error: e.g. APP_DB=sqlite and APP_DB__HOST=...
                        # In this case, we prefer the nested one or log/raise.
                        # For now, let's reset to dict to allow nesting.
                        current[part] = {}
                    current = current[part]

                last_part = parts[-1]
                if last_part in current and isinstance(current[last_part], dict):
                    # Overlap: we have a scalar but there was already a dict.
                    # Ignore the scalar or merge?
                    # Usually, more specific (deeper) config is preferred.
                    pass
                else:
                    current[last_part] = value
        return env_config

    def load_cli_args(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Loads configuration from CLI arguments (e.g., --database.port=5432)."""
        if args is None:
            args = sys.argv[1:]

        cli_config = {}
        for arg in args:
            if arg.startswith("--"):
                if "=" in arg:
                    key_val = arg[2:]
                    parts = key_val.split("=", 1)
                    key_path = parts[0]
                    value = parts[1]
                else:
                    key_path = arg[2:]
                    value = "true"

                parts = key_path.split(".")
                current = cli_config
                for i, part in enumerate(parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    elif not isinstance(current[part], dict):
                        current[part] = {}
                    current = current[part]

                last_part = parts[-1]
                if not (last_part in current and isinstance(current[last_part], dict)):
                    current[last_part] = value
        return cli_config

    def load(
        self,
        default_config: Optional[Dict[str, Any]] = None,
        config_files: Optional[List[str]] = None,
        cli_args: Optional[List[str]] = None
    ) -> 'Config':
        """
        Loads configuration from all sources following the priority hierarchy.
        Hierarchy: Default < Base Files < Profile Files < Env < CLI

        Args:
            default_config (Optional[Dict[str, Any]]): Base default configuration.
            config_files (Optional[List[str]]): List of filenames to load from base_path.
            cli_args (Optional[List[str]]): Explicit CLI arguments to parse.

        Returns:
            Config: A Config wrapper around the merged configuration data.
        """
        # Deep copy to avoid side effects on the passed default_config
        config = copy.deepcopy(default_config) if default_config else {}
        self._default_config = copy.deepcopy(default_config) if default_config else {}
        self._last_loaded_files = config_files.copy() if config_files else []
        self._last_cli_args = cli_args # Stored to persist during hot-reloads

        self.config_files = []
        profile_files: List[Path] = []

        if config_files:
            # First pass: load all base files
            for file_name in config_files:
                path = self.base_path / file_name
                if path.exists():
                    self.config_files.append(path)
                    file_data = self.load_file(path)
                    self._merge_dicts(config, file_data)

                # Identify profile-specific files for the second pass
                stem = path.stem
                suffix = path.suffix
                # If path.name is ".env", stem is "" and suffix is ".env"
                # -> profile_file_name should be ".env.dev"
                if not stem and suffix == ".env":
                    profile_file_name = f".env.{self.profile}"
                else:
                    profile_file_name = f"{stem}.{self.profile}{suffix}"

                profile_path = path.parent / profile_file_name
                if profile_path.exists():
                    profile_files.append(profile_path)

            # Second pass: load all profile-specific files (higher precedence)
            for p_path in profile_files:
                self.config_files.append(p_path)
                profile_data = self.load_file(p_path)
                self._merge_dicts(config, profile_data)

        # 2. Load from environment variables (higher precedence than files)
        env_data = self.load_environment()
        self._merge_dicts(config, env_data)

        # 3. Load from CLI arguments (highest precedence)
        cli_data = self.load_cli_args(cli_args)
        self._merge_dicts(config, cli_data)

        # 4. Validate schema if provided
        if self.schema:
            config = self.schema.validate(config)

        self._raw_config = config
        return Config(config, self)

    def watch(self, interval: float = 1.0):
        """
        Starts watching loaded configuration files for changes.
        When a change is detected, reloads the config (persisting CLI overrides) and calls callbacks.

        Args:
            interval (float): Polling interval in seconds.
        """
        if self._watcher:
            self._watcher.stop()

        def _reload_callback():
            # Re-load with the same parameters, including CLI args to ensure they persist
            new_config = self.load(
                default_config=self._default_config,
                config_files=self._last_loaded_files,
                cli_args=self._last_cli_args
            )
            for cb in self._on_reload_callbacks:
                cb(new_config)

        self._watcher = ConfigWatcher(
            file_paths=self.config_files,
            callback=_reload_callback,
            interval=interval
        )
        self._watcher.start()

    def on_reload(self, callback: Callable[['Config'], None]):
        """Registers a callback for when the configuration is hot-reloaded."""
        self._on_reload_callbacks.append(callback)

    def stop_watching(self):
        """Stops the file watcher if it is running."""
        if self._watcher:
            self._watcher.stop()
            self._watcher = None

    def load_from_files_only(self) -> Dict[str, Any]:
        """
        Utility for diffing: loads configuration strictly from files and defaults.
        Maintains correct precedence: Default < Base Files < Profile Files.
        """
        config = copy.deepcopy(self._default_config)
        profile_files = []

        for file_name in self._last_loaded_files:
            path = self.base_path / file_name
            if path.exists():
                file_data = self.load_file(path)
                self._merge_dicts(config, file_data)

            stem = path.stem
            suffix = path.suffix
            if not stem and suffix == ".env":
                profile_file_name = f".env.{self.profile}"
            else:
                profile_file_name = f"{stem}.{self.profile}{suffix}"

            profile_path = path.parent / profile_file_name
            if profile_path.exists():
                profile_files.append(profile_path)

        for p_path in profile_files:
            profile_data = self.load_file(p_path)
            self._merge_dicts(config, profile_data)

        if self.schema:
            try:
                config = self.schema.validate(config)
            except:
                pass # Allow invalid for diffing purposes
        return config

class Config:
    """
    A wrapper around configuration data providing dot-notation access and diffing capabilities.
    """
    def __init__(self, data: Dict[str, Any], loader: Optional[ConfigLoader] = None):
        """
        Initializes the Config wrapper.

        Args:
            data (Dict[str, Any]): The configuration data.
            loader (Optional[ConfigLoader]): The loader that produced this configuration.
        """
        self._data = data
        self._loader = loader

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Access configuration using dot notation (e.g., 'database.host').

        Args:
            key_path (str): The dot-separated key path.
            default (Any): The default value if the key is not found.

        Returns:
            Any: The configuration value or default.
        """
        parts = key_path.split(".")
        current = self._data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def __getattr__(self, name: str) -> Any:
        """Enables dot-notation access to configuration keys."""
        if name in self._data:
            val = self._data[name]
            if isinstance(val, dict):
                return Config(val, self._loader)
            return val
        raise AttributeError(f"'Config' object has no attribute '{name}'")

    def to_dict(self) -> Dict[str, Any]:
        """Returns the raw configuration as a dictionary."""
        return self._data

    def diff(self) -> Dict[str, Any]:
        """
        Compares currently used configuration with what is currently in source files.
        Shows differences introduced by Environment Variables, CLI arguments, or recent file changes.

        Returns:
            Dict[str, Any]: A dictionary detailing the changes.
        """
        if not self._loader:
            return {}

        file_config = self._loader.load_from_files_only()
        return self._calculate_diff(self._data, file_config)

    def _calculate_diff(self, current: Any, file_cfg: Any) -> Dict[str, Any]:
        """Recursively calculates the diff between two configuration structures."""
        diff = {}
        if not isinstance(current, dict) or not isinstance(file_cfg, dict):
            if current != file_cfg:
                return {"current": current, "file": file_cfg, "status": "modified"}
            return {}

        all_keys = set(current.keys()) | set(file_cfg.keys())
        for k in all_keys:
            if k not in file_cfg:
                diff[k] = {"current": current[k], "file": None, "status": "added_or_env_cli"}
            elif k not in current:
                diff[k] = {"current": None, "file": file_cfg[k], "status": "removed"}
            else:
                if isinstance(current[k], dict) and isinstance(file_cfg[k], dict):
                    nested_diff = self._calculate_diff(current[k], file_cfg[k])
                    if nested_diff:
                        diff[k] = nested_diff
                elif current[k] != file_cfg[k]:
                    diff[k] = {"current": current[k], "file": file_cfg[k], "status": "modified"}
        return diff
