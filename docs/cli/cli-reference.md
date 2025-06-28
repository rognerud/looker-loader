# CLI Reference

The Looker Loader command-line interface provides a simple way to generate LookML files from your BigQuery tables.

## Basic Usage

```bash
uv run looker_loader [OPTIONS]
```

Or if installed with pip:

```bash
looker_loader [OPTIONS]
```

## Command Options

### Global Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--config` | - | string | `.` | Path to the config files directory |
| `--output-dir` | `-o` | string | `./output` | Output directory for generated LookML files |
| `--table` | `-t` | string | - | Generate LookML for specific table only |
| `--lex` | - | flag | `false` | Enable Lexicanum integration |

### Option Details

#### `--config`

Specify the directory containing your configuration files:

```bash
# Use current directory (default)
uv run looker_loader

# Use specific directory
uv run looker_loader --config /path/to/config

# Use relative path
uv run looker_loader --config ./my_config
```

The config directory should contain:
- `loader_config.yml` - BigQuery connections and loader settings
- `loader_recipe.yml` - Field transformation rules
- `lexicanum.yml` - Field definitions (optional)

#### `--output-dir` / `-o`

Specify where generated LookML files should be saved:

```bash
# Use default output directory
uv run looker_loader

# Use custom output directory
uv run looker_loader --output-dir ./my_lookml_files

# Use absolute path
uv run looker_loader -o /path/to/lookml/output
```

#### `--table` / `-t`

Generate LookML for a specific table only:

```bash
# Generate for all tables (default)
uv run looker_loader

# Generate for specific table
uv run looker_loader --table fct_sales

# Generate for table with custom output
uv run looker_loader -t dim_customers -o ./customers_only
```

#### `--lex`

Enable Lexicanum integration for enhanced field labeling:

```bash
# Without Lexicanum (default)
uv run looker_loader

# With Lexicanum
uv run looker_loader --lex
```