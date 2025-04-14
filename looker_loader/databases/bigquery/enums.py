from looker_loader.enums import ExtendedEnum

class BigqueryUrl(str, ExtendedEnum):
    BIGQUERY = "https://bigquery.googleapis.com/bigquery/v2/projects/{project_id}/datasets/{dataset_id}/tables/{table_id}"

class BigqueryMode(str, ExtendedEnum):
    REPEATED = "REPEATED"

class BigqueryType(str, ExtendedEnum):
    RECORD = "RECORD"
    ARRAY = "ARRAY"
    STRUCT = "STRUCT"

class BigqueryMapping(str, ExtendedEnum):
    FLOAT = "number"
    FLOAT64 = "number"
    NUMERIC = "number"
    BIGNUMERIC = "number"
    BOOLEAN = "yesno"
    STRING = "string"
    TIMESTAMP = "timestamp"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "string"  
    BOOL = "yesno"
    GEOGRAPHY = "string"
    BYTES = "string"
    ARRAY = "string"
    STRUCT = "string"
    JSON = "string"