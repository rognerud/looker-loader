import google.auth
from google.auth.transport.requests import Request
import requests

from looker_loader.models.database import DatabaseTable

from looker_loader.databases.bigquery.enums import BigqueryMode, BigqueryType, BigqueryUrl
import httpx
import logging

class BigQueryDatabase:
    def __init__(self):
        """Initialize the BigQueryDatabase class."""
        self.database_type = "bigquery"

    def init(self):
        """Authenticate the user with Google Cloud using default credentials."""
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
        self.init()
        url = BigqueryUrl.BIGQUERY.value.format(
            project_id=project_id, dataset_id=dataset_id, table_id=table_id
        )

        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()

        self.json_schema = response.json()

    async def _async_fetch_table_schema(self, project_id: str, dataset_id: str, table_id: str):
        """Fetch schema data for a table"""
        # logging.info("Fetching schema for table '%s'", table_id)

        url = BigqueryUrl.BIGQUERY.value.format(
            project_id=project_id, dataset_id=dataset_id, table_id=table_id
        )
        async with httpx.AsyncClient() as client:
            data = await client.get(url, headers=self.headers, timeout=10)  # Await the response and get the content
        return data.json()  # Return the JSON content

    def _parse_schema(self, json) -> DatabaseTable:
        """Parse the schema of a BigQuery table into a Pydantic model."""
        table_ref = json.get("tableReference")
        fields = json.get("schema").get("fields")

        return DatabaseTable(
            name=table_ref.get("tableId"),
            table_group=table_ref.get("datasetId"),
            table_project=table_ref.get("projectId"),
            fields=fields,
            sql_table_name=f'{table_ref.get("projectId")}.{table_ref.get("datasetId")}.{table_ref.get("tableId")}',
        )

    def get_table_schema(self, project_id, dataset_id, table_id) -> DatabaseTable:
        """get the schema of a bigquery table and parse it into a common database schema."""
        logging.info("Fetching schema for table '%s'", table_id)
        json_schema = self._fetch_table_schema(project_id, dataset_id, table_id)
        return self._parse_schema(json_schema)

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
