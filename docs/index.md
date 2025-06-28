# Looker Loader Documentation

Welcome to the Looker Loader documentation! Looker Loader is a powerful Python package that automatically generates LookML files from your BigQuery tables, making it easy to create and maintain Looker views and explores.

## What is Looker Loader?

Looker Loader is a tool that:

- **Automatically generates LookML** from your BigQuery table schemas
- **Applies intelligent rules** to create meaningful dimensions and measures
- **Supports custom recipes** for specialized field transformations
- **Integrates with Lexicanum** for enhanced field labeling
- **Provides a simple CLI** for easy automation

## Key Features

- 🚀 **Automatic LookML Generation**: Convert BigQuery tables to Looker views instantly
- 📊 **Smart Field Detection**: Automatically identify primary keys, dates, numbers, and more
- 🎯 **Custom Recipes**: Define rules for how different field types should be handled
- 🏷️ **Lexicanum Integration**: Use AI-powered field labeling for better user experience
- ⚙️ **Flexible Configuration**: Support for multiple projects, datasets, and table filtering
- 🔧 **CLI Interface**: Simple command-line tool for automation and CI/CD integration

## Quick Start

1. **Install the package**:
   ```bash
   uv add looker_loader
   ```

2. **Create configuration files**:
   - `loader_config.yml` - Define your BigQuery connections and settings
   - `loader_recipe.yml` - Define rules for field transformations

3. **Run the loader**:
   ```bash
   uv run looker_loader
   ```

## Documentation Structure

- **[Getting Started](getting-started/installation.md)**: Installation and basic setup
- **[Configuration](configuration/loader-config.md)**: Detailed configuration guides
- **[CLI Reference](cli/cli-reference.md)**: Complete command-line interface documentation
- **[Advanced Topics](advanced/recipes.md)**: Custom recipes and advanced features
- **[API Reference](api/models.md)**: Programmatic API documentation

## Example Configuration

Here's a simple example of what your configuration might look like:

```yaml
# loader_config.yml
config:
  loader:
    lexicanum: true
    output_path: ./views
  bigquery:
    - project_id: "my-project"
      dataset_id: "my_dataset"
      config:
        regex_include: "^fct_|^dim_"
```

```yaml
# loader_recipe.yml
recipes:
  - name: primary_key
    filters:
      field_order: [0]
    dimension:
      primary_key: true
```

## Getting Help

- 📖 **Documentation**: This site contains comprehensive guides and references
- 🐛 **Issues**: Report bugs or request features on [GitHub](https://github.com/your-username/looker-loader/issues)
- 💬 **Discussions**: Join the conversation in [GitHub Discussions](https://github.com/your-username/looker-loader/discussions)

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/your-username/looker-loader/blob/main/CONTRIBUTING.md) for details on how to get started. 