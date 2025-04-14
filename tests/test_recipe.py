from looker_loader.cli import Cli
from tests.fixtures.bigquery import bigquery_schema_1
from looker_loader.models.looker import Looker, LookerDim
from rich import print
cli = Cli()
cli._load_recipe("tests/fixtures/basic")

def get_fields(thing, fields=[]):
    """Get the fields from a schema"""
    for field in thing.fields:
        dimensions = cli.mixer.apply_mixture(field)
        if not isinstance(dimensions, list):
            parsed = LookerDim(**dimensions.model_dump())
            fields.append(parsed)
        else:
            for dim in dimensions:
                parsed = LookerDim(**dim.model_dump())
                fields.append(parsed)
    return fields

def test_get_fields(bigquery_schema):
    """Test the get_fields function"""
    # print(bigquery_schema)
    fields = get_fields(bigquery_schema)
    print(fields)

bq = bigquery_schema_1()
test_get_fields(bq)