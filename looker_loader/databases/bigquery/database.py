import google.auth
from google.auth.transport.requests import Request
import requests

from looker_loader.models.database import DatabaseTable

from looker_loader.databases.bigquery.enums import BigqueryMode, BigqueryType, BigqueryUrl

import logging

class BigQueryDatabase:
    def __init__(self):
        """Initialize the BigQueryDatabase class."""
        self.database_type = "bigquery"
        credentials, _ = google.auth.default()
        credentials.refresh(Request())
        self.headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

    def _fetch_table_schema(
        self, project_id: str, dataset_id: str, table_id: str
    ) -> DatabaseTable:
        """Fetch the schema of a BigQuery table and parse it into a Pydantic model."""

        url = BigqueryUrl.BIGQUERY.value.format(
            project_id=project_id, dataset_id=dataset_id, table_id=table_id
        )

        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()

        self.json_schema = response.json()

    def _parse_schema(self) -> DatabaseTable:
        """Parse the schema of a BigQuery table into a Pydantic model."""
        self.parsed_schema = DatabaseTable(name=self.json_schema.get("table_id"), fields=self.json_schema["schema"]["fields"])

    def get_table_schema(self, project, dataset, table_id) -> DatabaseTable:
        """get the schema of a bigquery table and parse it into a common database schema."""
        self._fetch_table_schema(project, dataset, table_id)
        self._parse_schema()

        return self.parsed_schema

    def get_tables_in_dataset(self, project_id: str, dataset_id: str) -> list[DatabaseTable]:
        """Get all tables in a BigQuery dataset."""

        from google.cloud import bigquery
        client = bigquery.Client()
        dataset_url = f"{project_id}.{dataset_id}"
        tables = client.list_tables(dataset_url)

        table_list = []
        for table in tables:
            table_list.append(table.table_id)
        return table_list # Make an API request.
