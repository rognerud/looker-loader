# Loader Configuration

The `loader_config.yml` file is the main configuration file for Looker Loader. It defines your BigQuery connections, loader settings, and table filtering rules.

## File Structure

```yaml
config:
  loader:
    # Loader-specific settings
  bigquery:
    # BigQuery connection configurations
```

## Loader Configuration

The `loader` section contains global settings for the Looker Loader:

### Possible Settings

```yaml
config:
  loader:
    lexicanum: true                    # Enable Lexicanum integration
    output_path: ./views              # Output directory for LookML files
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `lexicanum` | boolean | `false` | Enable Lexicanum for enhanced field labeling |
| `output_path` | string | `./output` | Directory where LookML files will be generated |

## BigQuery Configuration

The `bigquery` section contains one or more BigQuery dataset configurations:

### Basic BigQuery Configuration

```yaml
config:
  bigquery:
    - project_id: "your-project-id"
      dataset_id: "your_dataset"
      table_id:
        - "table_1" # Optional: specific tables to process
      config:
        # Dataset-specific configuration
```

### Advanced BigQuery Configuration

```yaml
config:
  bigquery:
    - project_id: "your-project-id"
      dataset_id: "your_dataset"
      config:
        regex_include: "^fct_|^dim_"  # Include tables matching pattern
        regex_exclude: "_temp$"       # Exclude tables matching pattern
        prefix_files: "pre_"          # Prefix for generated file names
        prefix_views: "pre_"          # Prefix for view names
        explore: true                 # Generate explore files
        unstyled: false              # Generate unstyled views
```

### Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `project_id` | string | Yes | Google Cloud project ID |
| `dataset_id` | string | Yes | BigQuery dataset ID |
| `tables` | array | No | Specific tables to process (if empty, processes all tables) |
| `config.regex_include` | string | No | Regex pattern to include tables |
| `config.regex_exclude` | string | No | Regex pattern to exclude tables |
| `config.prefix_files` | string | No | Prefix for generated file names |
| `config.prefix_views` | string | No | Prefix for view names in LookML |
| `config.explore` | boolean | No | Generate explore files (default: `true`) |
| `config.unstyled` | boolean | No | Generate unstyled views (default: `false`) |

## Complete Examples

### Simple Configuration

```yaml
config:
  loader:
    lexicanum: true
    output_path: ./views
  bigquery:
    - project_id: "my-analytics-project"
      dataset_id: "analytics_data"
      config:
        regex_include: "^fct_|^dim_"
```

### Multiple Datasets

```yaml
config:
  loader:
    lexicanum: true
    output_path: ./views
  bigquery:
    - project_id: "my-project"
      dataset_id: "sales_data"
      config:
        regex_include: "^fct_sales|^dim_"
        prefix_files: "sales_"
    
    - project_id: "my-project"
      dataset_id: "marketing_data"
      config:
        regex_include: "^fct_marketing|^dim_"
        prefix_files: "marketing_"
```

### Complex Filtering

```yaml
config:
  loader:
    lexicanum: true
    output_path: ./views
  bigquery:
    - project_id: "my-project"
      dataset_id: "production_data"
      config:
        regex_include: "^fct_|^dim_|^obt_"
        regex_exclude: "_temp$|_backup$|_test$"
        prefix_files: "prod_"
        prefix_views: "prod_"
        explore: true
        unstyled: false
```

### Specific Tables Only

```yaml
config:
  loader:
    lexicanum: false
    output_path: ./views
  bigquery:
    - project_id: "my-project"
      dataset_id: "analytics"
      tables:
        - "fct_daily_sales"
        - "dim_customers"
        - "dim_products"
      config:
        explore: true
```

## Environment-Specific Configurations

### Development Environment and Prod Environment

```yaml
config:
  bigquery:
    - project_id: "my-project"
      dataset_id: "dev_data"
      config:
        prefix_files: "dev_"
        prefix_views: "dev_"
    - project_id: "my-project"
      dataset_id: "prod_data"
      config:
        prefix_files: ""
        prefix_views: ""
```