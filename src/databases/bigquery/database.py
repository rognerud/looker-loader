import google.auth
from google.auth.transport.requests import Request
import requests
from src.databases.bigquery.models.bigqueryTable import (
    BigQueryTableSchema,
    BigQueryFieldSchema,
)

from src.models.database import DatabaseField, DatabaseTable

from src.databases.bigquery.enums import BigqueryMode, BigqueryType, BigqueryUrl

class BigQueryDatabase:
    def _fetch_table_schema(
        self, project_id: str, dataset_id: str, table_id: str
    ) -> BigQueryTableSchema:
        """Fetch the schema of a BigQuery table and parse it into a Pydantic model."""
        credentials, _ = google.auth.default()

        credentials.refresh(Request())

        url = BigqueryUrl.BIGQUERY.value.format(
            project_id=project_id, dataset_id=dataset_id, table_id=table_id
        )

        headers = {"Authorization": f"Bearer {credentials.token}"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        table_info = response.json()

        schema = BigQueryTableSchema(fields=table_info["schema"]["fields"])

        return schema

    def _recurse_types(self, field: BigQueryFieldSchema, include_name=False) -> str:
        """Recursively parse the type of a field, by including nested fields in type."""
        if field.type == BigqueryType.RECORD.value:
            inner_types = []
            for sub_field in field.fields:
                inner_types.append(self._recurse_types(sub_field, include_name=True))
            if field.mode == BigqueryMode.REPEATED.value:
                type = f"{BigqueryType.ARRAY.value}<{BigqueryType.STRUCT.value}<{', '.join(inner_types)}>>"
            else:
                type = f"{BigqueryType.STRUCT.value}<{', '.join(inner_types)}>"
        else:
            if field.mode == BigqueryMode.REPEATED.value:
                type = f"{BigqueryType.ARRAY.value}<{field.type}>"
            else:
                type = field.type

        if include_name:
            type = f"{field.name} {type}"
        return type

    def _recursively_flatten_fields(self, fields: list[BigQueryFieldSchema], prefix=""):
        """Recursively flatten the fields of a schema, moving nested fields to the top level."""
        flat_fields = []
        for field in fields:
            field.name = prefix + field.name
            if field.fields:
                flat_fields.extend(
                    self._recursively_flatten_fields(field.fields, field.name + ".")
                )
            flat_fields.append(field)
        return flat_fields

    def _recurse_type_fields(self, fields):
        """Recursively adjust the type of fields and nested fields to match dbt catalog format."""
        for field in fields:
            field.type = self._recurse_types(field)
            if field.fields:
                self._recurse_type_fields(field.fields)

    def _translate_schema_to_dbt_model(
        self, schema: BigQueryTableSchema
    ) -> dict:
        """Translate a BigQueryTableSchema to a dbt model schema."""

        self._recurse_type_fields(schema.fields)
        schema.fields = self._recursively_flatten_fields(schema.fields)

        dict_schema = schema.model_dump()
        catalog_nodes = []
        for field in dict_schema.get("fields"):
            catalog_nodes.append(field)
        catalog_schema = {}
        catalog_schema["columns"] = catalog_nodes

        return DatabaseTable(**catalog_schema)

    def get_table_schema(self, project, dataset, table_id) -> BigQueryTableSchema:
        """get the schema of a dbt table and parse it into a common dbt model schema."""
        schema = self._fetch_table_schema(project, dataset, table_id)
        catalog_schema = self._translate_schema_to_dbt_model(schema)

        return catalog_schema

    def split_table_id(self, table_id):
        """Split a table_id into project, dataset, and table."""
        project, dataset, table = table_id.split(".")
        return project, dataset, table