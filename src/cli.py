import argparse
import os
import lkml
import logging
from rich.logging import RichHandler
# from importlib.metadata import version
from src.utils import FileHandler

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
        parser.add_argument(
            "--implicit-primary-key",
            help="Add this flag to set primary keys on views based on the first field",
            action="store_true",
            default=False,
        )
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

        if not args.table:
            logging.error("Please provide a table name")
            return
        
        from src.databases.bigquery.database import BigQueryDatabase 
        db = BigQueryDatabase()
        a,b,c = db.split_table_id(table_id=args.table)
        schema = db.get_table_schema(a,b,c)
        import rich
        rich.print(schema)


def main():
    cli = Cli()
    cli.run()


if __name__ == "__main__":
    main()
