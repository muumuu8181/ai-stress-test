# Multi-format Config Loader

A flexible configuration loader for Python that supports multiple formats, schema validation, environment variables, CLI arguments, and hot reloading.

## Features

- **Multi-format Support**: JSON, YAML (subset), TOML, INI, and .env.
- **Auto-detection**: Automatically detects format based on file extension.
- **Configuration Merging**: Follows a strict hierarchy: Default < Files < Profile-specific Files < Environment Variables < CLI Arguments.
- **Schema Validation**: Type checking, required fields, range checks, and nested schemas.
- **Dot Notation**: Access nested configuration using `config.get("database.host")` or `config.database.host`.
- **Profile Support**: Easily switch between profiles (e.g., dev, staging, prod).
- **Hot Reloading**: Automatically reloads configuration when source files change.
- **Configuration Diff**: Compare currently used configuration with source files.

## Installation

No external dependencies are required (uses standard library only, except for `pytest` in development).

## Usage

### Basic Loading

```python
from config_loader import ConfigLoader

loader = ConfigLoader(base_path="config")
config = loader.load(
    default_config={"port": 8080},
    config_files=["settings.json", "overrides.yaml"]
)

print(config.port)
print(config.get("database.host", "localhost"))
```

### Schema Validation

```python
from config_loader import ConfigLoader, Validator, SchemaField

schema = Validator({
    "port": SchemaField(int, required=True, min_val=1024, max_val=65535),
    "debug": SchemaField(bool, default=False),
    "database": Validator({
        "host": SchemaField(str, required=True),
        "user": SchemaField(str, default="admin")
    })
})

loader = ConfigLoader(schema=schema)
config = loader.load(config_files=["config.json"])
```

### Environment Variables and CLI Arguments

By default, it looks for environment variables with the prefix `APP_`.
Nesting is supported using `__`.

- Env: `APP_DATABASE__HOST=db.local` -> `config.database.host`
- CLI: `--database.host=db.local` -> `config.database.host`

```python
# Custom prefix
loader = ConfigLoader(env_prefix="MYAPP_")
config = loader.load()
```

### Hot Reloading

```python
loader = ConfigLoader()
config = loader.load(config_files=["config.json"])

def on_reload(new_config):
    print("Config updated!", new_config.to_dict())

loader.on_reload(on_reload)
loader.watch(interval=1.0) # Starts background thread
```

### Profile Support

If the profile is `dev`, loading `config.json` will also automatically attempt to load `config.dev.json` and merge it.

```python
loader = ConfigLoader(profile="prod")
config = loader.load(config_files=["config.json"])
```

### Diff Display

```python
diff = config.diff()
for key, change in diff.items():
    print(f"Key {key}: {change['status']} (Current: {change['current']}, File: {change['file']})")
```

## Quality Standards

- **Tests**: Comprehensive test suite including unit, integration, and edge cases.
- **Coverage**: > 80% test coverage.
- **Type Hints**: Fully type-annotated public API.
- **Standard Library**: Built using only Python standard library components (JSON, tomllib, configparser, etc.).
