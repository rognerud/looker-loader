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
    apply_recipe: Optional[List[str]] = Field(
        default=[],
        description="List of recipe names to apply to the dataset"
    )
    exclude_recipe: Optional[List[str]] = Field(
        default=[],
        description="List of recipe names to exclude from the dataset"
    )
    explores_as_extensions: Optional[bool] = Field(
        default=False,
        description="Whether to create explores as extensions"
    )
    include_descriptions: Optional[bool] = Field(
        default=True,
        description="Whether to create descriptions for views and fields"
    )
    field_types: Optional[List[str]] = Field(
        default=None,
        description="List of field types to include"
    )

class LoaderConfig(BaseModel):
    """Loader configuration model for Looker Loader"""
    lexicanum: Optional[bool] = Field(
        default=False,
        description="Whether to use lexicanum for loading Looker data"
    )
    output_path: Optional[str] = Field(
        default="./output",
        description="Path where the Looker data will be output"
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
    loader: Optional[LoaderConfig] = Field(
        default_factory=LoaderConfig,
    )