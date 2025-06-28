# Installation

This guide will help you install and set up Looker Loader for your project.

## Prerequisites

Before installing Looker Loader, make sure you have:

- **Python 3.8+** installed on your system
- **BigQuery access** with appropriate permissions
- **Looker instance** where you'll deploy the generated LookML

## Installation Methods

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver. It's the recommended way to install Looker Loader.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add looker_loader to your project
uv add looker_loader
```

### Using pip

```bash
pip install looker_loader
```

### Using Poetry

```bash
poetry add looker_loader
```

## BigQuery Authentication

Looker Loader needs access to your BigQuery datasets. You have several authentication options:

### Option 1: Application Default Credentials (Recommended)

Set up Google Cloud SDK and authenticate:

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth application-default login
```

### Option 2: Service Account Key

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

### Option 3: Workload Identity (for GKE)

If running in Google Kubernetes Engine, you can use Workload Identity for authentication.

## Verify Installation

After installation, verify that Looker Loader is working:

```bash
# Check if the package is installed
python -c "import looker_loader; print('Looker Loader installed successfully!')"

# Check CLI help
uv run looker_loader --help
```

## Next Steps

Once installed, you can:

1. **[Create your first configuration](quick-start.md)** - Set up your `loader_config.yml` and `loader_recipe.yml` files
2. **[Run your first generation](quick-start.md)** - Generate LookML from your BigQuery tables
3. **[Explore advanced features](../advanced/recipes.md)** - Learn about custom recipes and advanced configurations

## Troubleshooting

### Common Issues

**Import Error: No module named 'looker_loader'**
- Make sure you're in the correct virtual environment
- Verify the package was installed successfully: `pip list | grep looker_loader`

**BigQuery Authentication Error**
- Check your Google Cloud credentials: `gcloud auth list`
- Verify your service account has the necessary BigQuery permissions
- Ensure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set correctly

**Permission Denied Errors**
- Make sure your service account has the following roles:
  - `BigQuery Data Viewer`
  - `BigQuery Job User`
  - `BigQuery Metadata Viewer`

### Getting Help

If you encounter issues not covered here:

- Check the [GitHub Issues](https://github.com/your-username/looker-loader/issues) for known problems
- Create a new issue with detailed error messages and your environment information
- Join our [Discussions](https://github.com/your-username/looker-loader/discussions) for community support 