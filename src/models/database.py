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
    name: str

    columns: Optional[List[DatabaseField]]
    labels: Optional[List[str]] = None
    tags: Optional[List[str]] = None
