from typing import List, Optional, Union
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError

class DatabaseField(BaseModel):
    name: str
    type: str

    description: Optional[str] = None
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    mode: Optional[str] = None

class DatabaseTable(BaseModel):
    name: str = None
    type: str = None

    description: Optional[str] = None
    columns: Optional[List[DatabaseField]] = None
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
