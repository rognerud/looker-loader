from typing import Union
import google.auth
from google.auth.transport.requests import Request
import requests
import google.api_core.exceptions
from looker_loader.models.database import DatabaseTable
from looker_loader.databases.bigquery.enums import BigqueryMode, BigqueryType, BigqueryUrl
import httpx
import logging
from google.auth.impersonated_credentials import Credentials as ImpersonatedCredentials
from google.auth.transport.requests import Request
from google.auth import default
from google.cloud import bigquery # Import bigquery client here

class BigQueryDatabase:
    def __init__(self):
        """Initialize the BigQueryDatabase class."""
        self.database_type = "bigquery"
        self.credentials = None # Add this line to store credentials

    def init(self, impersonate_service_account: str = None):
        """Authenticate the user with Google Cloud using default credentials."""
        if impersonate_service_account:
            logging.debug(f"Impersonating service account: {impersonate_service_account}")
            # 1. Get the "source" credentials (the identity performing the impersonation).
            # These can be your user credentials, another service account, etc.
            # The source credentials must have the 'Service Account Token Creator' role
            # on the target_principal service account.
            source_credentials, _ = default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            # 2. Create ImpersonatedCredentials.
            # target_scopes should specify the permissions the impersonated service account needs.
            self.credentials = ImpersonatedCredentials( # Store credentials in self.credentials
                source_credentials=source_credentials,
                target_principal=impersonate_service_account,
                target_scopes=["https://www.googleapis.com/auth/cloud-platform"], # Or more specific scopes
                lifetime=3600  # Optional: token lifetime in seconds (default is 3600, max is 43200)
            )
        else:
            logging.debug("Using default credentials without impersonation.")
            self.credentials, _ = default() # Store credentials in self.credentials

        self.credentials.refresh(Request())
        self.headers = {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "application/json",
        }

    async def _async_fetch_table_schema(self, project_id: str, dataset_id: str, table_id: str, config=None) -> tuple[dict, dict]:
        """Fetch schema data for a table"""
        logging.getLogger("httpx").setLevel(logging.WARNING)
        url = BigqueryUrl.BIGQUERY.value.format(
            project_id=project_id, dataset_id=dataset_id, table_id=table_id
        )
        async with httpx.AsyncClient() as client:
            data = await client.get(url, headers=self.headers, timeout=10)
        if data.status_code != 200:
            logging.error(f"Error fetching table schema: {project_id}.{dataset_id}.{table_id} - {data.text}")
            return {}, config
        return data.json(), config

    def _parse_schema(self, json) -> DatabaseTable:
        """Parse the schema of a BigQuery table into a Pydantic model."""
        table_ref = json.get("tableReference")
        fields = json.get("schema").get("fields")
        clustering_fields = json.get("clustering", {}).get("fields", [])
        add_clustering_to_fields = []
        for field in fields:
            if field.get("name") in clustering_fields:
                logging.debug(f"Field {field.get('name')} is clustered.")
                field["is_clustered"] = True
            add_clustering_to_fields.append(field)
        return DatabaseTable(
            name=table_ref.get("tableId"),
            table_group=table_ref.get("datasetId"),
            table_project=table_ref.get("projectId"),
            fields=add_clustering_to_fields,
            sql_table_name=f'{table_ref.get("projectId")}.{table_ref.get("datasetId")}.{table_ref.get("tableId")}',
        )

    def get_tables_in_dataset(self, project_id: str, dataset_id: str) -> list[str]:
        """Get all tables in a BigQuery dataset."""
        # Ensure credentials are set before attempting to use them
        if not self.credentials:
            logging.error("Credentials not initialized. Call .init() first.")
            return []

        # Pass the credentials explicitly to the BigQuery client
        client = bigquery.Client(credentials=self.credentials, project=project_id) # MODIFIED LINE
        
        try:
            # list_tables expects a DatasetReference, not a string
            dataset_ref = client.dataset(dataset_id, project=project_id) # MODIFIED LINE
            tables = client.list_tables(dataset_ref) # MODIFIED LINE
            table_list = []
            for table in tables:
                table_list.append(table.table_id)
            return table_list
        except google.api_core.exceptions.NotFound as e:
            logging.error(f"Dataset {project_id}.{dataset_id} not found: {e}")
            return []
        except Exception as e: # Catch other potential errors, like Forbidden
            logging.error(f"Error listing tables in dataset {project_id}.{dataset_id}: {e}")
            return []