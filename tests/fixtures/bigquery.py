from looker_loader.databases.bigquery.database import BigQueryDatabase
import json
import pytest

fixture_1 = """
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

@pytest.fixture
def bigquery_schema_1():
    """Fixture for BigQuery schema"""
    db = BigQueryDatabase()
    db.json_schema = json.loads(fixture_1)
    db._parse_schema()
    return db.parsed_schema


fixture_2 = """
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
        "name": "duration_seconds",
        "type": "INTEGER",
        "description": "x."
      }
    ]
  }
}
"""

@pytest.fixture
def bigquery_schema_2():
    """Fixture for BigQuery schema"""
    db = BigQueryDatabase()
    db.json_schema = json.loads(fixture_2)
    db._parse_schema()
    return db.parsed_schema
