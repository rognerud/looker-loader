from pydantic import BaseModel, model_validator
from typing import List, Optional, Dict
import logging

class DatabaseField(BaseModel):
    name: str
    type: str
    mode: Optional[str] = None
    fields: Optional[List["DatabaseField"]] = None
    description: Optional[str] = None
    parent_name: Optional[str] = None
    parent_type: Optional[str] = None
    sql: Optional[str] = None

    @model_validator(mode="before")
    def create(cls, values):
        if hasattr(values, "fields"):
            inherited_children = []
            for child in values.get("field"):
                child["parent_type"] = values.get("type")
                if hasattr(values, "parent_name"):
                    child["parent_name"] = f"{values.get('parent_name')}.{values.get('name')}"
                else:
                    child["parent_name"] = values.get("name")
                inherited_children.append(DatabaseField(**child))
            values["fields"] = inherited_children

        base = "${TABLE}"
        if hasattr(values, "parent_type") and values.parent_type == "RECORD":
            values["sql"] = values["name"]
        else:
            values["sql"] = f"{base}.{values["name"]}"

        return values

    class Config:
        from_attributes = True


class DatabaseTable(BaseModel):
    fields: List[DatabaseField]
    type: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    class Config:
        from_attributes = True
