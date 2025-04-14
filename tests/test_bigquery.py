from tests.fixtures.bigquery import bigquery_schema_1

def test_bigquery_schema(bigquery_schema_1):
    """Test the BigQuery schema"""
    assert bigquery_schema_1 is not None
    assert len(bigquery_schema_1.fields) == 2
    assert bigquery_schema_1.fields[0].name == "pk_obt"
    assert bigquery_schema_1.fields[1].name == "weekly_data"
    assert len(bigquery_schema_1.fields[1].fields) == 5
    assert bigquery_schema_1.fields[1].fields[0].name == "question_cohort_week_id"
    assert bigquery_schema_1.fields[1].fields[3].name == "number_of_people"
    assert bigquery_schema_1.fields[1].fields[4].name == "answer_value_response_information"
    assert len(bigquery_schema_1.fields[1].fields[4].fields) == 2
    assert bigquery_schema_1.fields[1].fields[4].fields[0].name == "question_cohort_week_answer_id"
    assert bigquery_schema_1.fields[1].fields[4].fields[1].name == "answer_value"
