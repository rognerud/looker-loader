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
from looker_loader.models.recipe import LookerMixture
from looker_loader.generator.lookml import LookmlGenerator
from looker_loader.tools.lkml_converter import convert_to_lkml
import asyncio

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
        logging.info(f"Writing LookML file to {file_path}")
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

    def _load_config(self, folder: str = None):
        """Load the config from a yaml file"""
        args = self._args_parser.parse_args()
        if folder is None:
            folder = args.config
        if not os.path.exists(folder):
            raise FileNotFoundError(f"Folder {folder} does not exist")

        logging.info(f"Loading Config from {folder}/loader_config.yml")
        data = self._file_handler.read(f"{folder}/loader_config.yml", file_type="yaml")
        self.config = Config(**data['config'])

    def _load_tables(self):
        """Load the schemas from the database"""
        process_list = []

        for d in self.config.bigquery:
            if not d.tables:
                logging.info("Finding all tables")
                tables = self.database.get_tables_in_dataset(d.project_id, d.dataset_id)
            else:
                tables = d.tables

            for table in tables:
                
                process_list.append(
                    {
                        "project_id": d.project_id,
                        "dataset_id": d.dataset_id,
                        "table_id": table,
                    }
                )

        self.tables = process_list

    async def get_schemas(self):
        """
            asyncronously fetch the schemas of the tables
            and parse them into a common database schema
            and store them in self.schemas
        """
        self.database.init()
        tasks = [
            self.database._async_fetch_table_schema(
            project_id=table.get("project_id"),
            dataset_id=table.get("dataset_id"),
            table_id=table.get("table_id"),
            )
            for table in self.tables
            ]
        
        # Run all tasks concurrently and gather the results
        results = await asyncio.gather(*tasks)

        schemas = []
        for json in results:
            schemas.append(self.database._parse_schema(json))

        self.schemas = schemas

    def run(self):
        """Run the CLI"""
        args = self._args_parser.parse_args()
        self.database = BigQueryDatabase()
        self.lookml = LookmlGenerator(cli_args=args)

        self._load_recipe()
        self._load_config()
        self._load_tables()

        asyncio.run(self.get_schemas())

        mixures = []
        for schema in self.schemas:
            logging.info(f"Generating LookML for '{schema.name}'")

            mixture = self.mixer.mixturize(schema)
            mixures.append(mixture)

        # insert lexical parsing and interaction with lexicanum here.

        for mixture in mixures:

            views, explore = self.lookml.generate(
                model=mixture,
            )
            logging.info(f"Generated {len(views)} views")
            self._write_lookml_file(
                output_dir=f'output/{schema.table_group}',
                file_path=f'{mixture.name}.view.lkml',
                contents=convert_to_lkml(views, explore),
            )

        logging.info("LookML files generated successfully")

def main():
    cli = Cli()
    cli.run()

if __name__ == "__main__":
    main()