import argparse
import os
import logging
import yaml
from rich.logging import RichHandler
from looker_loader.utils import FileHandler
from looker_loader.models.recipe import CookBook
from looker_loader.models.config import Config
from looker_loader.databases.bigquery.database import BigQueryDatabase
from looker_loader.tools import recipe_mixer
logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)


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

    def run(self):
        """Run the CLI"""
        args = self._args_parser.parse_args()

        logging.info("Loading Recipe")
        folder = args.config
        data = self._file_handler.read(f"{folder}/loader_recipe.yml", file_type="yaml")
        recipe = CookBook(**data) 

        # logging.info(recipe)

        logging.info("Loading Config")
        config = self._file_handler.read(f"{folder}/loader_config.yml", file_type="yaml")
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

        mixer = recipe_mixer.RecipeMixer(recipe)

        def get_fields(thing, fields=[], measures=[]):
            """Get the fields from a schema"""
            for field in thing.fields:
                base_dimension, dimensions, measures = mixer.apply_mixture(field)

                if field.fields:
                    base_dimension.fields = get_fields(field)
                
                fields.append(base_dimension)
                if dimensions:
                    fields.extend(dimensions)
            return fields, measures

        for scheme in schemas:
            fields, measures = get_fields(scheme)
            logging.info(fields)
            logging.info(measures)

def main():
    cli = Cli()
    cli.run()


if __name__ == "__main__":
    main()