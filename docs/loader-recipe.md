# Loader Recipe Configuration

The `loader_recipe.yml` file defines rules for how different field types should be transformed into LookML dimensions and measures. Recipes allow you to automatically apply consistent patterns to your BigQuery fields.

## File Structure

```yaml
recipes:
  - name: recipe_name
    filters:
      # Field filtering criteria
    dimension:
      # Dimension properties
      measures:
        # measures for the dimension
      variants:
        # Additional field variants
```

## Recipe Components

### Name

Each recipe must have a unique name that describes its purpose:

```yaml
recipes:
  - name: primary_key
    # recipe configuration
```

### Filters

Each recipe must have at least one filter that defines what fields the rule applies to.
Filters define which fields the recipe applies to. Multiple filters can be combined:

```yaml
filters:
  field_order: [0]           # Field position in schema
  types: [string, number]    # BigQuery data types
  db_types: [STRING, INT64]  # BigQuery database types
  regex_include: "_id$"      # Include fields matching pattern
  regex_exclude: "_temp$"    # Exclude fields matching pattern
```

### Dimension

The `dimension` section defines how the field should be configured in LookML:

```yaml
dimension:
  primary_key: true          # Mark as primary key
  hidden: true              # Hide from users
  group_label: "Identifiers" # Group label
  value_format_name: id     # Value format
  timeframes: [date, week]  # Time dimensions
  measures: []              # Auto-generated measures
```

### Variants

Variants creates derived fields based on the original field:

You can use {{ jinja2 }} syntax to reference information from the parent dimension.
The fields of a parent entity can be referenced as:
- {{ parent_name }}
- {{ parent_label }}
- {{ parent_group_label }}
for sql you can define ${{{ parent_name }}} to reference the parent field.
It renders into the lookml code as ${parent_name}

Certain attributes like group_label and value_format_name are inherited to variants.

```yaml
dimension:
  variants:
    - suffix: minutes
      remove: _seconds
      sql: ${{{ parent_name }}} / 60
      type: number
```


### Measures

Automatically generate measures for the dimension.
You can use {{ jinja2 }} syntax to reference information from the parent dimension.
The fields of a parent entity can be referenced as:

```yaml
dimension:
  measures:
    - type: count_distinct  # Count distinct values
    - type: sum            # Sum of values
    - type: count          # Count of records
```

Measures can be created for variants as well!
```yaml
dimension:
  variant:
    suffix: divided_by_three
    sql: ${{{ parent_name }}} / 3
    measures:
      - type: sum  # Count distinct values
```

## Filter Options

### Field Order

Filter by the position of the field in the table schema:

```yaml
filters:
  field_order: [0]          # First field only
  field_order: [0, 1, 2]    # First three fields
```

### Data Types

Filter by Looker data types:

```yaml
filters:
  types: [string]           # String fields only
  types: [number, integer]  # Numeric fields
  types: [date, timestamp]  # Date/time fields
  types: [boolean]          # Boolean fields
```

### Database Types

Filter by specific BigQuery database types:

```yaml
filters:
  db_types: [STRING]        # STRING fields only
  db_types: [INT64, FLOAT64] # Integer and float fields
  db_types: [RECORD]        # Record/nested fields
```

### Regex Patterns

Filter fields using regular expressions:

```yaml
filters:
  regex_include: "_id$"     # Fields ending with _id
  regex_exclude: "_temp$"   # Exclude fields ending with _temp
```

## Dimension Properties

### Basic Properties
You can add much of the looker specific syntax for dimensions or dimension groups to a dimension in a recipe:

```yaml
dimension:
  primary_key: true         # Mark as primary key
  hidden: true             # Hide from users
  group_label: "Identifiers" # Group label for organization
  value_format_name: id    # Value format (id, decimal_1, etc.)
  label: "Custom Label"    # Custom field label ( recommended to use jinja2)
  description: "Custom description"
```

### Time Dimensions

For date/time fields, you can specify the timeframes:

```yaml
dimension:
  timeframes:
    - raw                   # Raw value
    - time                  # Time only
    - time_of_day          # Time of day
    - week_of_year         # Week of year
```

## Complete Recipe Examples

### Primary Key Recipe

```yaml
recipes:
  - name: primary_key
    filters:
      field_order: [0]
    dimension:
      primary_key: true
```

### Hide Record Fields

```yaml
recipes:
  - name: hide_records
    filters:
      db_types: [RECORD]
    dimension:
      hidden: true
```

### ID Fields

```yaml
recipes:
  - name: group_ids
    dimension:
      group_label: Identifiers
      value_format_name: id
      measures:
        - type: count_distinct
    filters:
      regex_include: _id$|^pk.*_|_code$
```

### Numeric Fields

```yaml
recipes:
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
```

### Hide fields that start with _

```yaml
recipes:
  - name: _hidden
    filters:
      regex_include: ^_
    dimension:
      hidden: true
```

### Time Duration Fields

```yaml
recipes:
  - name: time_second_values
    filters:
      regex_include: _seconds$
      types: [number]
    dimension:
      group_label: Durations
      value_format_name: decimal_0
      variants:
        - suffix: minutes
          remove: _seconds
          sql: ${ {{ parent_name }} } / 60
          measures:
            - type: sum
```

### Date Fields

```yaml
recipes:
  - name: time_date_values
    filters:
      regex_include: _date
      types: [date]
    dimension:
      variants:
        - suffix: iso_year
          type: number
          remove: _date
          sql: Extract(isoyear from ${{{ parent_name }}})
        - suffix: iso_week
          type: number
          remove: _date
          sql: Extract(isoweek from ${{{ parent_name }}})
```

### Boolean Fields with custom html styling

```yaml
recipes:
  - name: yesno
    filters:
      types: [yesno]
    dimension:
      group_label: Yes/No
      html: >-
          <a href='#drillmenu' target='_self'>
            {% if value == 'Yes' %}
            <span style='color:#B2AEFF;text-align:center;'>✔</span><span> Yes </span>
            {% else %}
            <span style='color:#F9A4A9;text-align:center;'>✖</span><span> No </span>
            {% endif %}
          </a>
```

## Best Practices

### 1. Start with Generic Recipes

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
```
