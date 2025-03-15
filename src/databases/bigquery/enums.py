from src.enums import ExtendedEnum

class BigqueryUrl(str, ExtendedEnum):
    BIGQUERY = "https://bigquery.googleapis.com/bigquery/v2/projects/{project_id}/datasets/{dataset_id}/tables/{table_id}"

class BigqueryMode(str, ExtendedEnum):
    REPEATED = "REPEATED"

class BigqueryType(str, ExtendedEnum):
    RECORD = "RECORD"
    ARRAY = "ARRAY"
    STRUCT = "STRUCT"