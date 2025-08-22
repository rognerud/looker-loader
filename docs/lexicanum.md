# Lexicanum Integration

Lexicanum is a powerful feature in Looker Loader that enhances field labeling and final adjustments of labels and other information on a field name basis.

## What is Lexicanum?

Lexicanum is a field definition system that:

- **Provides human-readable labels** for technical field names
- **Maintains consistency** across your Looker instance
- **Improves user experience** with better field names and descriptions

## Basic Usage

### Enable Lexicanum

Enable Lexicanum in your configuration:

```yaml
# loader_config.yml
config:
  loader:
    lexicanum: true
```

Or use the CLI flag:

```bash
uv run looker_loader --lex
```

### Create Lexicanum File

Enabling lexicanum creates a `lexicanum.yml` file in your configuration directory:

It will contain a empty entry for every unique field name in your loaded tables.
```yaml
# lexicanum.yml
customer_id:
  label: null
order_amount:
  label: null
product_name:
  label: null
```

Any looker attribute for fields can be added to the lexicanum.
It will be merged with the recipe files for each field as the latest entry, taking precedence when building the dimensions and metrics.
