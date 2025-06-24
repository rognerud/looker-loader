from typing import List, Optional, Union
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

class DatasetConfig(BaseModel):
    """Dataset configuration model for Looker Loader"""
    prefix_views: Optional[str] = Field(
        default="",
        description="Prefix to be added to all table names in the dataset"
    )
    suffix_views: Optional[str] = Field(
        default="",
        description="Suffix to be added to all table names in the dataset"
    )
    prefix_files: Optional[str] = Field(
        default="",
        description="Prefix to be added to all file names in the dataset"
    )
    suffix_files: Optional[str] = Field(
        default="",
        description="Suffix to be added to all file names in the dataset"
    )
    regex_include: Optional[str] = Field(
        default=None,
        description="Regex pattern to match table names for loading"
    )
    regex_exclude: Optional[str] = Field(
        default=None,
        description="Regex pattern to exclude table names from loading"
    )
    explore: Optional[bool] = Field(
        default=True,
        description="Whether to create an explore for the dataset"
    )
    unstyled: Optional[bool] = Field(
        default=False,
        description="Whether to create unstyled views for the dataset"
    )


class BigQuery(BaseModel):
    """BigQuery model for Looker Loader"""
    project_id: str
    dataset_id: str
    config: DatasetConfig = Field(default_factory=DatasetConfig, description="Dataset Configuration")
    tables: Optional[List[str]] = Field(default=None, description="List of tables to load")

class Config(BaseModel):
    """Config model for Looker Loader"""
    bigquery: List[BigQuery]