# Quick Start

This guide will walk you through creating your first Looker Loader configuration and generating LookML files from your BigQuery tables.

## Step 1: Create Configuration Files

Create two configuration files in your project root:

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

## Step 2: Run the Loader

Execute the Looker Loader command:

```bash
uv run looker_loader
```

Or if you installed with pip:

```bash
looker_loader
```

## Step 3: Check the Output

The loader will create LookML files in your specified output directory (default: `./views`). You should see files like:

```
views/
├── fct_sales.view.lkml
├── dim_customers.view.lkml
└── obt_daily_summary.view.lkml
```

## Step 4: Deploy to Looker

1. Copy the generated `.view.lkml` files to your Looker project
2. Commit and push the changes
3. Looker will automatically validate and deploy the new views

## Advanced Usage

### Generate for Specific Tables

To generate LookML for specific tables only:

```bash
uv run looker_loader --table fct_sales
```

### Use Custom Output Directory

```bash
uv run looker_loader --output-dir ./my_lookml_files
```

### Enable Lexicanum for Better Labels

If you have a `lexicanum.yml` file with field definitions:

```bash
uv run looker_loader --lex
```

## Example Output

Here's what a generated LookML file might look like:

```lookml
view: fct_sales {
  sql_table_name: `your-project-id.your_dataset.fct_sales` ;;

  dimension: order_id {
    type: string
    primary_key: yes
    group_label: "Identifiers"
  }

  dimension: order_date {
    type: date
    timeframes: [raw, time, date, week, month, quarter, year]
    group_label: "Dates"
  }

  dimension: total_amount {
    type: number
    value_format_name: decimal_1
    group_label: "Numbers"
  }

  measure: count_distinct_order_id {
    type: count_distinct
    sql: ${order_id} ;;
    label: "Count Distinct Order ID"
  }

  measure: sum_total_amount {
    type: sum
    sql: ${total_amount} ;;
    label: "Sum Total Amount"
  }
}
```

## Next Steps

Now that you have the basics working:

- **[Explore Configuration Options](../configuration/loader-config.md)** - Learn about all available configuration settings
- **[Create Custom Recipes](../advanced/recipes.md)** - Build specialized field transformation rules
- **[Use Lexicanum](../advanced/lexicanum.md)** - Enhance field labeling with AI-powered suggestions
- **[CLI Reference](../cli/cli-reference.md)** - Master all command-line options

## Troubleshooting

### Common Issues

**No tables found**
- Check your `project_id` and `dataset_id` are correct
- Verify your BigQuery permissions
- Check if your `regex_include` pattern matches any tables

**Authentication errors**
- Ensure your Google Cloud credentials are properly set up
- Check the [Installation Guide](installation.md) for authentication options

**Empty output files**
- Verify your recipes match your table schema
- Check the logs for any filtering that might be excluding all fields

For more help, see the [Troubleshooting section](installation.md#troubleshooting) in the Installation Guide. 