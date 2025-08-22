# available as a python package https://pypi.org/project/looker_loader/

## automatically refresh table views, and create rules for how you want your data to be loaded into looker

## Quick Start

1. **Install the package**:
   ```bash
   uv add looker_loader
   ```

2. **Create configuration files**:
   - `loader_config.yml` - Define your BigQuery connections and settings
   - `loader_recipe.yml` - Define rules for field transformations


### loader_config.yml

This file defines your BigQuery connections and loader settings:

```yaml
config:
  loader:
    lexicanum: true
    output_path: ./views
  bigquery:
    - project_id: "your-project-id"
      dataset_id: "your_dataset"
      config:
        regex_include: "^fct_|^dim_|^obt_"
        regex_exclude: "_temp$|_backup$"
```

### loader_recipe.yml

This file defines rules for how different field types should be transformed:

```yaml
recipes:
  - name: primary_key
    filters:
      field_order: [0]
    dimension:
      primary_key: true

  - name: hide_records
    filters:
      db_types: [RECORD]
    dimension:
      hidden: true

  - name: group_ids
    dimension:
      group_label: Identifiers
      value_format_name: id
      measures:
        - type: count_distinct
    filters:
      regex_include: _id$|^pk.*_|_code$

  - name: numbers
    filters:
      types: [number]
      regex_exclude: _id$|^pk_|_code$
    dimension:
      group_label: Numbers
      value_format_name: decimal_1
      measures:
        - type: sum
          label: "Sum {{ parent_label }}"

  - name: time_date_values
    filters:
      regex_include: _date
      types: [date]
    dimension:
      timeframes:
        - raw
        - time
        - date
        - week
        - month
        - quarter
        - year
```


3. **Run the loader**:
   ```bash
   uv run looker_loader
   ```



##  Check the Output

The loader will create LookML files in your specified output directory (default: `./views`). You should see files like:

```
views/
├── fct_sales.view.lkml
├── dim_customers.view.lkml
└── obt_daily_summary.view.lkml
```


### Common Issues

**No tables found**
- Check your `project_id` and `dataset_id` are correct
- Verify your BigQuery permissions
- Check if your `regex_include` pattern matches any tables

**Authentication errors**
- Ensure your Google Cloud credentials are properly set up
- Check the [Installation Guide](installation.md) for authentication options

## Next Steps

Now that you have the basics working:

- **[Explore Configuration Options](../docs/loader-config.md)** - Learn about all available configuration settings
- **[Create Custom Recipes](../docs/loader-recipe.md)** - Build specialized field transformation rules
- **[Use Lexicanum](../docs/lexicanum.md)** - Enhance field definitions by using a common source of truth
