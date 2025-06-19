# work in progress

## define rules for loading data and automatically apply it when loading the data in looker

### intended features
- write rules for how to format columns
- write rules for generating derived columns and measures
- refresh tables using cicd
- leverage llm to translate names and descriptions using locales, in a editable way

### how to run:
uv add looker_loader

define a loader_config.yml file
config:
  bigquery:
    - project_id: "project_name"
      dataset_id: "dataset_name"
      tables:
        - "table_name"

define a loader_recipe.yml file
recipes:
  - name: primary_key
    filters:
      field_order:
        - 0
    dimension:
      primary_key: true

uv run looker_loader
