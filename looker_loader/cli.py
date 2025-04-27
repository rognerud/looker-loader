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

    def _load_schemas(self):
        """Load the schemas from the database"""
        schemas = []
        b = BigQueryDatabase()

        for d in self.config.bigquery:
            if not d.tables:
                logging.info("Finding all tables")
                tables = b.get_tables_in_dataset(d.project_id, d.dataset_id)
            else:
                tables = d.tables
            
            logging.info(f"Loading Schemas {tables} from '{d.project_id}.{d.dataset_id}'")
            for table in tables:
                logging.info(f"Loading Schema for '{table}'")
                schema = b.get_table_schema(d.project_id, d.dataset_id, table)
                schemas.append(schema)

        self.schemas = schemas

    def run(self):
        """Run the CLI"""
        args = self._args_parser.parse_args()

        self._load_recipe()
        self._load_config()

        self._load_schemas()
        lookml = LookmlGenerator(cli_args=args)

        for scheme in self.schemas:
            logging.info(f"Generating LookML for '{scheme.name}'")

            mixture = self.mixer.mixturize(scheme)
            logging.info(f"Mixture length: {len(mixture.model_dump())}")
            r = lookml.generate(
                model=mixture,
            )

            logging.info(f"r length: {len(r)}")
            self._write_lookml_file(
                output_dir=f'output/{scheme.table_group}',
                file_path=f'{scheme.name}.view.lkml',
                contents=convert_to_lkml(r),
            )

        logging.info("LookML files generated successfully")

def main():
    cli = Cli()
    cli.run()

if __name__ == "__main__":
    main()