from typing import List, Optional, Union
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

class DatabaseField(BaseModel):
    name: str
    type: str

    description: Optional[str] = None
    append_description: Optional[str] = None
    prepend_description: Optional[str] = None

    labels: Optional[List[str]] = None
    append_labels: Optional[List[str]] = None
    prepend_labels: Optional[List[str]] = None

    tags: Optional[List[str]] = None
    append_tags: Optional[List[str]] = None
    prepend_tags: Optional[List[str]] = None

class Table(BaseModel):
    name: str
    type: str

    description: Optional[str] = None
    fields: Optional[List[DatabaseField]] = None
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
