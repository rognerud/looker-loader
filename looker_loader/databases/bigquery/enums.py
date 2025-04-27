from looker_loader.enums import ExtendedEnum

class BigqueryUrl(ExtendedEnum):
    BIGQUERY = "https://bigquery.googleapis.com/bigquery/v2/projects/{project_id}/datasets/{dataset_id}/tables/{table_id}"

class BigqueryMode(ExtendedEnum):
    REPEATED = "REPEATED"

class BigqueryType(ExtendedEnum):
    RECORD = "RECORD"
    ARRAY = "ARRAY"
    STRUCT = "STRUCT"