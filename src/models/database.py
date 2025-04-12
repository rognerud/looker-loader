from pydantic import BaseModel
from typing import List, Optional, Dict


class DatabaseField(BaseModel):
    name: str
    type: str
    mode: Optional[str] = None
    fields: Optional[List["DatabaseField"]] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class DatabaseTable(BaseModel):
    fields: List[DatabaseField]
    type: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    class Config:
        from_attributes = True
