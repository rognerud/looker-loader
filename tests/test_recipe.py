from looker_loader.cli import Cli
from tests.fixtures.bigquery import bigquery_schema_1
from looker_loader.models.looker import Looker, LookerDim
from rich import print
cli = Cli()
cli._load_recipe("tests/fixtures/basic")


def test_cli():
    """Test the CLI"""
    cli = Cli()
    cli._load_recipe("tests/fixtures/basic")
    assert cli.recipe != None