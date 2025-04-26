import argparse
import os
import logging
import lkml
from rich.logging import RichHandler
from looker_loader.utils import FileHandler
from looker_loader.models.recipe import CookBook
from looker_loader.models.config import Config
from looker_loader.databases.bigquery.database import BigQueryDatabase
from looker_loader.tools import recipe_mixer
from looker_loader.models.looker import Looker, LookerDim
from looker_loader.generator.lookml import LookmlGenerator

logging.basicConfig(
    level=logging.DEBUG, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

def remove_empty_from_dict(data):
  """Recursively removes keys with None or empty list values from a dictionary.

  Args:
    data: The dictionary to clean.

  Returns:
    A new dictionary with empty values removed.
  """
  if isinstance(data, dict):
    return {
        k: remove_empty_from_dict(v)
        for k, v in data.items()
        if v is not None and (not isinstance(v, list) or len(v) > 0)
    }
  elif isinstance(data, list):
    return [remove_empty_from_dict(item) for item in data if item is not None and (not isinstance(item, list) or len(item) > 0)]
  else:
    return data

class Cli:
    HEADER = """
    Load your data into looker
    """

    def __init__(self):
        self._args_parser = self._init_argparser()
        self._file_handler = FileHandler()

    def _init_argparser(self):
        """Create and configure the argument parser"""
        parser = argparse.ArgumentParser(
            description=self.HEADER,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.set_defaults(
            build_explore=True, write_output=True, hide_arrays_and_structs=True
        )
        parser.add_argument(
            "--table","-t",
            help="The name of the table to generate LookML for",
            type=str,
        )
        parser.add_argument(
            "--config",
            help="Path to the config file",
            type=str,
            default=".",
        )
        # parser.add_argument(
        #     "--version",
        #     action="version",
        #     version=f'looker-loader {version("looker-loader")}',
        # )
        # parser.add_argument(
        #     "--output-dir",
        #     help="Path to a directory that will contain the generated lookml files",
        #     default=self.DEFAULT_LOOKML_OUTPUT_DIR,
        #     type=str,
        # )
        return parser

    def _write_lookml_file(
        self,
        output_dir: str,
        file_path: str,
        contents: str,
    ) -> str:
        """Write LookML content to a file."""

        file_name = os.path.basename(file_path)
        file_path = os.path.join(output_dir, file_path.split(file_name)[0])
        os.makedirs(file_path, exist_ok=True)

        file_path = f"{file_path}/{file_name}"

        # Write contents
        self._file_handler.write(file_path, contents)

        return file_path

    def _load_recipe(self, folder: str = None):
        """Load the recipe from a yaml file"""
        args = self._args_parser.parse_args()
        if folder is None:
            folder = args.config
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Folder {folder} does not exist")

        logging.info(f"Loading Recipe from {folder}/loader_recipe.yml")
        data = self._file_handler.read(f"{folder}/loader_recipe.yml", file_type="yaml")
        self.recipe = CookBook(**data)
        self.mixer = recipe_mixer.RecipeMixer(self.recipe)

    def run(self):
        """Run the CLI"""
        args = self._args_parser.parse_args()

        self._load_recipe()

        # logging.info(recipe)

        logging.info("Loading Config")
        config = self._file_handler.read(f"{args.config}/loader_config.yml", file_type="yaml")
        # config = Config(**config)
        config = Config(**config['config'])

        schemas = []
        b = BigQueryDatabase()

        for d in config.bigquery:
            # logging.info(d)
            if not d.tables:
                # logging.info("Finding all tables")
                tables = b.get_tables_in_dataset(d.project_id, d.dataset_id)
            else:
                tables = d.tables

            for table in tables:
                schema = b.get_table_schema(d.project_id, d.dataset_id, table)
                schemas.append(schema)

        def get_fields(thing, fields=[]):
            """Get the fields from a schema"""
            for field in thing.fields:
                dimensions = self.mixer.apply_mixture(field)
                if not isinstance(dimensions, list):
                    parsed = LookerDim(**dimensions.model_dump())
                    fields.append(parsed)
                else:
                    for dim in dimensions:
                        parsed = LookerDim(**dim.model_dump())
                        fields.append(parsed)
            return fields

        for scheme in schemas:
            fields = get_fields(scheme)
            
            model = Looker(**{
                "name": scheme.name,
                "fields": fields,
            })

            lookml = LookmlGenerator(cli_args=args)
            r = lookml.generate(
                model=model,
            )

            flat_r = []
            for thing in r:
                from rich import print


                t = remove_empty_from_dict(thing)

                # if t.get("name") == "obt_penetrace_tv2__weekly_data__answer_value_response_information":
                print(t)

                view = self._write_lookml_file(
                    output_dir='output',
                    file_path='test.view.lkml',
                    contents=lkml.dump(remove_empty_from_dict(t)),
                )

def main():
    cli = Cli()
    cli.run()


if __name__ == "__main__":
    main()