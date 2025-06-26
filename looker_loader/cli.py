import argparse
import os
import logging
import lkml
import re
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
import yaml
from looker_loader.models.lex import Lex

logging.basicConfig(
    level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)

class Cli:
    HEADER = """
    Load your data into looker
    """

    def __init__(self):
        self.DEFAULT_LOOKML_OUTPUT_DIR = "output"
        self._args_parser = self._init_argparser()
        self._file_handler = FileHandler()
        self.args = self._args_parser.parse_args()
        self.lexicanum = None
        self.recipe = None


    def _init_argparser(self):
        """Create and configure the argument parser"""
        parser = argparse.ArgumentParser(
            description=self.HEADER,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        parser.set_defaults(
            llm=False, lex=False
        )
        parser.add_argument(
            "--table","-t",
            help="The name of the table to generate LookML for",
            type=str,
        )
        parser.add_argument(
            "--config",
            help="Path to the config files",
            type=str,
            default=".",
        )
        parser.add_argument(
            "--lex",
            help="Use lexicanum to generate LookML",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--llm",
            help="Use a LLM to generate labels in lexicanum",
            action="store_true",
            default=False,
        )
        # parser.add_argument(
        #     "--version",
        #     action="version",
        #     version=f'looker-loader {version("looker-loader")}',
        # )
        parser.add_argument(
            "--output-dir","-o",
            help="Path to a directory that will contain the generated lookml files",
            default=self.DEFAULT_LOOKML_OUTPUT_DIR,
            type=str,
        )
        return parser

    def _write_lookml_file(
        self,
        output_dir: str,
        file_path: str,
        contents: str,
    ) -> str:
        """Write LookML content to a file."""
        logging.debug(f"Writing LookML file to {file_path}")
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
            if not d.project_id or not d.dataset_id:
                raise ValueError(
                    f"Project ID and Dataset ID are required for BigQuery configuration: {d}"
                )

            if not d.tables:
                logging.info("Finding all tables in dataset %s", d.dataset_id)
                tables = self.database.get_tables_in_dataset(d.project_id, d.dataset_id)
            else:
                tables = d.tables

            for table in tables:
                if d.config.regex_include:
                    if re.search(
                        d.config.regex_include,
                        table,
                    ) is None:
                        logging.debug(
                            f"Table {table} excluded by regex {d.config.regex_include}")
                        continue
                if d.config.regex_exclude:
                    if re.search(
                        d.config.regex_exclude,
                        table,
                    ) is not None:
                        logging.debug(
                            f"Table {table} excluded by regex {d.config.regex_exclude}")
                        continue

                process_list.append(
                    {
                        "project_id": d.project_id,
                        "dataset_id": d.dataset_id,
                        "table_id": table,
                        "config": d.config
                    }
                )

        self.tables = process_list

    def _load_lexicanum(self):
        """Load the lexicanum from a yaml file"""
        try:
            with open('lexicanum.yml', 'r') as file:
                lex_fields = yaml.safe_load(file)
        except FileNotFoundError:
            logging.warning("lexicanum.yml file not found. Creating..")
            lex_fields = {}
        logging.info("Lexicanum is enabled. Collecting lexical fields from schemas...")

        for m in self.schemas:
            schema = m.get("schema")
            for field in schema.fields:
                if field.name in lex_fields.keys():
                    continue
                else:
                    lex_fields[field.name] = {'label': None}

        logging.debug("Lexical fields collected from mixtures, writing to lexicanum.yml")
        # Write to a YAML file
        with open('lexicanum.yml', 'w') as file:
            yaml.dump(lex_fields, file, sort_keys=True, allow_unicode=True)

        self.lexicanum = Lex(lex_fields)

    async def get_schemas(self):
        """
            asyncronously fetch the schemas of the tables
            and parse them into a common database schema
            and store them in self.schemas
        """
        tasks = [
            self.database._async_fetch_table_schema(
            project_id=table.get("project_id"),
            dataset_id=table.get("dataset_id"),
            table_id=table.get("table_id"),
            config=table.get("config")
            )
            for table in self.tables
            ]
        
        # Run all tasks concurrently and gather the results
        results = await asyncio.gather(*tasks)

        schemas = []
        for r in results:
            schemas.append({"schema":self.database._parse_schema(r[0]), "config": r[1]})

        self.schemas = schemas

    def _initialize_mixer(self):
        """Initialize the LookerMixture objects for each schema"""
        self.mixer = recipe_mixer.RecipeMixer(self.recipe, self.lexicanum)

    def run(self):
        """Run the CLI"""
        self.database = BigQueryDatabase()
        self.database.init()

        self.lookml = LookmlGenerator(cli_args=self.args)

        self._load_recipe()
        self._load_config()
        self._load_tables()

        # retrieve the schemas of the tables
        asyncio.run(self.get_schemas())

        if self.args.lex:
            self._load_lexicanum()

        self._initialize_mixer()

        mixtures = []
        for schema_object in self.schemas:
            schema = schema_object.get("schema")
            config = schema_object.get("config")

            mixture = self.mixer.mixturize(schema, config=config)
            mixtures.append({"mixture":mixture, "config": config, "table_group": schema.table_group})

        for m in mixtures:
            mixture = m.get("mixture")
            config = m.get("config")
            table_group = m.get("table_group")

            views, explore = self.lookml.generate(
                model=mixture,
                config=config,
            )
            self._write_lookml_file(
                output_dir=f'{self.args.output_dir}/{table_group}',
                file_path=f'{config.prefix_files}{mixture.name}{config.suffix_files}.view.lkml',
                contents=convert_to_lkml(views, explore),
            )

        logging.info("LookML files generated successfully")

def main():
    cli = Cli()
    cli.run()

if __name__ == "__main__":
    main()