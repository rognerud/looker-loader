from typing import List, Optional, Union
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

# Models for the configuration of Looker Loader

class BigQuery(BaseModel):
    """BigQuery model for Looker Loader"""
    project_id: str
    dataset_id: str
    tables: Optional[List[str]] = Field(default=None, description="List of tables to load")

class Config(BaseModel):
    """Config model for Looker Loader"""
    bigquery: List[BigQuery]