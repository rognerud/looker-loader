# Advanced Recipes

This guide covers advanced recipe patterns and complex use cases for Looker Loader.

## Complex Filtering Patterns

### Multi-Condition Filters

Combine multiple filter conditions for precise field targeting:

```yaml
recipes:
  - name: customer_metrics
    filters:
      types: [number]
      regex_include: "customer_.*_amount$"
      regex_exclude: "_temp$|_test$"
    dimension:
      group_label: "Customer Metrics"
      value_format_name: decimal_2
      measures:
        - type: sum
        - type: average
        - type: min
        - type: max
```

### Conditional Field Processing

Use field order and type combinations for specific processing:

```yaml
recipes:
  - name: first_string_field
    filters:
      field_order: [0]
      types: [string]
      regex_exclude: "^_"
    dimension:
      primary_key: true
      group_label: "Primary Identifiers"

  - name: second_numeric_field
    filters:
      field_order: [1]
      types: [number]
    dimension:
      group_label: "Secondary Metrics"
      value_format_name: decimal_1
```

## Advanced Variants

### Time-Based Variants

Create multiple time-based variants for date fields:

```yaml
recipes:
  - name: event_timestamps
    filters:
      regex_include: "_timestamp$|_created_at$|_updated_at$"
      types: [timestamp]
    dimension:
      timeframes:
        - raw
        - time
        - time_of_day
        - date
        - week
        - month
        - quarter
        - year
      variants:
        - suffix: date_only
          type: date
          remove: _timestamp
          sql: DATE(${{{ parent_name }}})
        - suffix: hour
          type: number
          remove: _timestamp
          sql: EXTRACT(HOUR FROM ${{{ parent_name }}})
        - suffix: day_of_week
          type: number
          remove: _timestamp
          sql: EXTRACT(DAYOFWEEK FROM ${{{ parent_name }}})
        - suffix: is_weekend
          type: yesno
          remove: _timestamp
          sql: CASE WHEN EXTRACT(DAYOFWEEK FROM ${{{ parent_name }}}) IN (1, 7) THEN 'Yes' ELSE 'No' END
```

### Aggregated Variants

Create variants that perform aggregations:

```yaml
recipes:
  - name: sales_amounts
    filters:
      regex_include: "_amount$|_revenue$|_sales$"
      types: [number]
    dimension:
      group_label: "Sales Metrics"
      value_format_name: decimal_2
      variants:
        - suffix: k
          type: number
          sql: ${{{ parent_name }}} / 1000
          label: "{{ parent_name.replace('_', ' ').title() }} (K)"
        - suffix: m
          type: number
          sql: ${{{ parent_name }}} / 1000000
          label: "{{ parent_name.replace('_', ' ').title() }} (M)"
        - suffix: percent_of_total
          type: number
          sql: SAFE_DIVIDE(${{{ parent_name }}}, SUM(${{{ parent_name }}}) OVER()) * 100
          label: "{{ parent_name.replace('_', ' ').title() }} (% of Total)"
```

## Conditional Logic

### Template-Based Conditions

Use Jinja2 templates for dynamic field processing:

```yaml
recipes:
  - name: conditional_labels
    filters:
      types: [string]
    dimension:
      label: "{% if 'id' in parent_name %}Identifier{% elif 'name' in parent_name %}Name{% else %}{{ parent_name.replace('_', ' ').title() }}{% endif %}"
      group_label: "{% if 'customer' in parent_name %}Customer{% elif 'product' in parent_name %}Product{% else %}General{% endif %} Information"
```

### Complex SQL Variants

Create variants with complex SQL logic:

```yaml
recipes:
  - name: status_fields
    filters:
      regex_include: "_status$|_state$"
      types: [string]
    dimension:
      group_label: "Status Fields"
      variants:
        - suffix: is_active
          type: yesno
          sql: |
            CASE 
              WHEN LOWER(${{{ parent_name }}}) IN ('active', 'enabled', 'yes', 'true', '1') THEN 'Yes'
              WHEN LOWER(${{{ parent_name }}}) IN ('inactive', 'disabled', 'no', 'false', '0') THEN 'No'
              ELSE 'Unknown'
            END
        - suffix: status_category
          type: string
          sql: |
            CASE 
              WHEN LOWER(${{{ parent_name }}}) IN ('active', 'enabled', 'running') THEN 'Active'
              WHEN LOWER(${{{ parent_name }}}) IN ('inactive', 'disabled', 'stopped') THEN 'Inactive'
              WHEN LOWER(${{{ parent_name }}}) IN ('pending', 'waiting') THEN 'Pending'
              ELSE 'Other'
            END
```

## Nested Field Processing

### Record Field Handling

Process nested record fields with custom logic:

```yaml
recipes:
  - name: nested_address_fields
    filters:
      db_types: [RECORD]
      regex_include: "address$|location$"
    dimension:
      hidden: true
      variants:
        - suffix: street
          type: string
          sql: ${{{ parent_name }}}.street
          label: "{{ parent_name.replace('_', ' ').title() }} Street"
        - suffix: city
          type: string
          sql: ${{{ parent_name }}}.city
          label: "{{ parent_name.replace('_', ' ').title() }} City"
        - suffix: state
          type: string
          sql: ${{{ parent_name }}}.state
          label: "{{ parent_name.replace('_', ' ').title() }} State"
        - suffix: zip_code
          type: string
          sql: ${{{ parent_name }}}.zip_code
          label: "{{ parent_name.replace('_', ' ').title() }} ZIP Code"
```

### Array Field Processing

Handle array fields with aggregation:

```yaml
recipes:
  - name: array_fields
    filters:
      db_types: [ARRAY]
    dimension:
      hidden: true
      variants:
        - suffix: count
          type: number
          sql: ARRAY_LENGTH(${{{ parent_name }}})
          label: "{{ parent_name.replace('_', ' ').title() }} Count"
        - suffix: first_item
          type: string
          sql: ${{{ parent_name }}}[OFFSET(0)]
          label: "{{ parent_name.replace('_', ' ').title() }} First Item"
        - suffix: last_item
          type: string
          sql: ${{{ parent_name }}}[OFFSET(ARRAY_LENGTH(${{{ parent_name }}}) - 1)]
          label: "{{ parent_name.replace('_', ' ').title() }} Last Item"
```

## Business Logic Recipes

### Customer Segmentation

Create customer segmentation based on multiple fields:

```yaml
recipes:
  - name: customer_segment
    filters:
      regex_include: "customer_id$"
    dimension:
      group_label: "Customer Analysis"
      variants:
        - suffix: segment
          type: string
          sql: |
            CASE 
              WHEN ${total_purchase_amount} > 10000 THEN 'High Value'
              WHEN ${total_purchase_amount} > 1000 THEN 'Medium Value'
              WHEN ${total_purchase_amount} > 0 THEN 'Low Value'
              ELSE 'No Purchases'
            END
          label: "Customer Segment"
        - suffix: loyalty_tier
          type: string
          sql: |
            CASE 
              WHEN ${days_since_first_purchase} > 365 THEN 'Long-term'
              WHEN ${days_since_first_purchase} > 90 THEN 'Medium-term'
              ELSE 'New'
            END
          label: "Loyalty Tier"
```

### Product Categories

Create product categorization logic:

```yaml
recipes:
  - name: product_category
    filters:
      regex_include: "product_id$"
    dimension:
      group_label: "Product Analysis"
      variants:
        - suffix: category
          type: string
          sql: |
            CASE 
              WHEN ${product_type} = 'electronics' THEN 'Electronics'
              WHEN ${product_type} = 'clothing' THEN 'Apparel'
              WHEN ${product_type} = 'books' THEN 'Books'
              ELSE 'Other'
            END
          label: "Product Category"
        - suffix: price_tier
          type: string
          sql: |
            CASE 
              WHEN ${price} > 100 THEN 'Premium'
              WHEN ${price} > 50 THEN 'Mid-range'
              WHEN ${price} > 10 THEN 'Budget'
              ELSE 'Economy'
            END
          label: "Price Tier"
```

## Performance Optimization Recipes

### Efficient Aggregations

Create optimized aggregation measures:

```yaml
recipes:
  - name: optimized_metrics
    filters:
      types: [number]
      regex_include: "_count$|_total$"
    dimension:
      group_label: "Optimized Metrics"
      measures:
        - type: sum
          sql: SUM(${{{ parent_name }}})
          label: "Total {{ parent_label }}"
        - type: average
          sql: AVG(${{{ parent_name }}})
          label: "Average {{ parent_label }}"
        - type: count_distinct
          sql: COUNT(DISTINCT ${{{ parent_name }}})
          label: "Distinct {{ parent_label }}"
```

### Partitioned Views

Handle partitioned tables efficiently:

```yaml
recipes:
  - name: partitioned_date
    filters:
      regex_include: "_date$|_partition_date$"
      types: [date]
    dimension:
      timeframes:
        - raw
        - date
        - week
        - month
        - quarter
        - year
      sql: |
        {% if 'partition' in parent_name %}
        DATE(${{{ parent_name }}})
        {% else %}
        ${{{ parent_name }}}
        {% endif %}
```

## Custom Value Formats

### Currency Formatting

Create currency-specific formatting:

```yaml
recipes:
  - name: currency_fields
    filters:
      regex_include: "_amount$|_price$|_cost$|_revenue$"
      types: [number]
    dimension:
      group_label: "Currency Fields"
      value_format_name: decimal_2
      variants:
        - suffix: formatted
          type: string
          sql: CONCAT('$', FORMAT('%.2f', ${{{ parent_name }}}))
          label: "{{ parent_name.replace('_', ' ').title() }} (Formatted)"
        - suffix: k_formatted
          type: string
          sql: CONCAT('$', FORMAT('%.1f', ${{{ parent_name }}} / 1000), 'K')
          label: "{{ parent_name.replace('_', ' ').title() }} (K)"
```

### Percentage Formatting

Handle percentage fields:

```yaml
recipes:
  - name: percentage_fields
    filters:
      regex_include: "_rate$|_percentage$|_pct$"
      types: [number]
    dimension:
      group_label: "Percentage Fields"
      value_format_name: percent_2
      variants:
        - suffix: formatted
          type: string
          sql: CONCAT(FORMAT('%.1f', ${{{ parent_name }}} * 100), '%')
          label: "{{ parent_name.replace('_', ' ').title() }} (Formatted)"
```

## Error Handling Recipes

### Null Value Handling

Create robust null value handling:

```yaml
recipes:
  - name: null_safe_fields
    filters:
      types: [string]
    dimension:
      sql: COALESCE(${{{ parent_name }}}, 'Unknown')
      label: "{{ parent_name.replace('_', ' ').title() }}"
      variants:
        - suffix: is_null
          type: yesno
          sql: CASE WHEN ${{{ parent_name }}} IS NULL THEN 'Yes' ELSE 'No' END
          label: "{{ parent_name.replace('_', ' ').title() }} Is Null"
```

### Data Validation

Add data validation measures:

```yaml
recipes:
  - name: validation_checks
    filters:
      types: [number]
    dimension:
      group_label: "Data Validation"
      variants:
        - suffix: is_negative
          type: yesno
          sql: CASE WHEN ${{{ parent_name }}} < 0 THEN 'Yes' ELSE 'No' END
          label: "{{ parent_name.replace('_', ' ').title() }} Is Negative"
        - suffix: is_zero
          type: yesno
          sql: CASE WHEN ${{{ parent_name }}} = 0 THEN 'Yes' ELSE 'No' END
          label: "{{ parent_name.replace('_', ' ').title() }} Is Zero"
```

## Best Practices

### Recipe Organization

1. **Order matters**: Put specific recipes before general ones
2. **Use descriptive names**: Make recipe purposes clear
3. **Group related recipes**: Keep similar recipes together
4. **Document complex logic**: Add comments for complex SQL

### Performance Considerations

1. **Limit variants**: Too many variants can impact performance
2. **Optimize SQL**: Use efficient SQL patterns
3. **Test thoroughly**: Validate complex recipes before production

### Maintenance

1. **Version control**: Track recipe changes
2. **Documentation**: Document business logic
3. **Testing**: Test recipes with sample data

## Next Steps

- **[Custom Dimensions](custom-dimensions.md)** - Create specialized field types
- **[Lexicanum Integration](lexicanum.md)** - Enhance field labeling
- **[Configuration Guide](../configuration/loader-recipe.md)** - Basic recipe configuration 