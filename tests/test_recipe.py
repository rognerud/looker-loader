from looker_loader.cli import Cli
from tests.fixtures.bigquery import bigquery_schema_2
from rich import print
cli = Cli()
cli._load_recipe("tests/fixtures/basic")

def get_fields(thing, fields=[], measures=[]):
    """Get the fields from a schema"""
    for field in thing.fields:
        base_dimension, dimensions, measures = cli.mixer.apply_mixture(field)

        fields.append(base_dimension)
        if dimensions:
            fields.extend(dimensions)
    return fields, measures

def test_get_fields(bigquery_schema):
    """Test the get_fields function"""
    print(bigquery_schema)
    fields, measures = get_fields(bigquery_schema)
    print(fields)
    print(measures)

bq = bigquery_schema_2()
test_get_fields(bq)