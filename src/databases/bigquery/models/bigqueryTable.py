from pydantic import BaseModel
from typing import List, Optional, Dict


class BigQueryFieldSchema(BaseModel):
    name: str
    type: str
    mode: Optional[str] = None
    fields: Optional[List["BigQueryFieldSchema"]] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class BigQueryTableSchema(BaseModel):
    fields: List[BigQueryFieldSchema]
    type: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    class Config:
        from_attributes = True
