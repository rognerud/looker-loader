# available as a python package https://pypi.org/project/looker_loader/

## automatically refresh table views, and create rules for how you want your data to be loaded into looker

### how to run:
uv add looker_loader

define a loader_config.yml file in your looker repository
config:
  bigquery:
    - project_id: "project_name"
      dataset_id: "dataset_name"
      tables:
        - "table_name"

define a loader_recipe.yml file in your looker repository
recipes:
  - name: primary_key
    filters:
      field_order:
        - 0
    dimension:
      primary_key: true

uv run looker_loader
