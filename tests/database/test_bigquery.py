from looker_loader.databases.bigquery.database import BigQueryDatabase
import json
import pytest

fixture = """
{
  "id": "project_id:dataset.table_id",
  "schema": {
    "fields": [
      {
        "name": "pk_obt",
        "type": "STRING",
        "description": "pk of the table"
      },
      {
        "name": "weekly_data",
        "type": "RECORD",
        "mode": "REPEATED",
        "fields": [
          {
            "name": "question_cohort_week_id",
            "type": "STRING",
            "description": "pk of the week"
          },
          {
            "name": "start_of_week",
            "type": "DATE",
            "description": ""
          },
          {
            "name": "duration_seconds",
            "type": "INTEGER",
            "description": "x."
          },
          {
            "name": "number_of_people",
            "type": "INTEGER",
            "description": ""
          },
          {
            "name": "answer_value_response_information",
            "type": "RECORD",
            "mode": "REPEATED",
            "fields": [
              {
                "name": "question_cohort_week_answer_id",
                "type": "STRING",
                "description": "pk of the answer"
              },
              {
                "name": "answer_value",
                "type": "STRING",
                "description": ""
              }
            ],
            "description": ""
          }
        ],
        "description": ""
      }
    ]
  }
}

"""
from rich import print

@pytest.fixture
def bigquery_schema():
    """Fixture for BigQuery schema"""
    db = BigQueryDatabase()
    db.json_schema = json.loads(fixture)
    db._parse_schema()
    return db.parsed_schema

def test_bigquery_schema(bigquery_schema):
    """Test the BigQuery schema"""
    assert bigquery_schema is not None
    assert len(bigquery_schema.fields) == 2
    assert bigquery_schema.fields[0].name == "pk_obt"
    assert bigquery_schema.fields[1].name == "weekly_data"
    assert len(bigquery_schema.fields[1].fields) == 5
    assert bigquery_schema.fields[1].fields[0].name == "question_cohort_week_id"
    assert bigquery_schema.fields[1].fields[3].name == "number_of_people"
    assert bigquery_schema.fields[1].fields[4].name == "answer_value_response_information"
    assert len(bigquery_schema.fields[1].fields[4].fields) == 2
    assert bigquery_schema.fields[1].fields[4].fields[0].name == "question_cohort_week_answer_id"
    assert bigquery_schema.fields[1].fields[4].fields[1].name == "answer_value"