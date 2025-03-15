from pydantic import BaseModel
from typing import List, Optional


class BigQueryFieldSchema(BaseModel):
    name: str
    type: str
    fields: Optional[List["BigQueryFieldSchema"]] = None
    mode: Optional[str] = None

    class Config:
        from_attributes = True


class BigQueryTableSchema(BaseModel):
    fields: List[BigQueryFieldSchema]

    class Config:
        from_attributes = True
