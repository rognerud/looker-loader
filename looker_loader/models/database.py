from pydantic import BaseModel, model_validator
from typing import List, Optional, Dict

# Models for database information loading

class DatabaseField(BaseModel):
    name: str
    type: str
    order: int
    mode: Optional[str] = None
    description: Optional[str] = None
    parent_name: Optional[str] = None
    parent_mode: Optional[str] = None
    parent_type: Optional[str] = None
    sql: Optional[str] = None
    fields: Optional[List["DatabaseField"]] = None

    @model_validator(mode="before")
    def push_down_attributes(cls, values):
        """ push parent_name, parent_mode and parent_type to children """
        if values.get("fields") is not None:
            inherited_children = []
            for child in values.get("fields"):
                child["parent_mode"] = values.get("mode")
                child["parent_type"] = values.get("type")
                if hasattr(values, "parent_name"):
                    child["parent_name"] = f"{values.get('parent_name')}.{values.get('name')}"
                else:
                    child["parent_name"] = values.get("name")
                inherited_children.append(DatabaseField(**child))
            values["fields"] = inherited_children
        return values
    
    @model_validator(mode="before")
    def push_order(cls, values):
        """ push order to children 
            order of the fields from the parent table
            is used to order the children fields
        """
        if values.get("fields") is not None:
            fields = []
            for i, field in enumerate(values.get("fields")):
                field["order"] = i
                fields.append(field)
            values["fields"] = fields
        return values

    @model_validator(mode="after")
    def create_sql(cls, values):
        """Create SQL field from name and parent_name"""
        base = "${TABLE}"
        if values.parent_mode == "REPEATED":
            values.sql = values.name
        else:
            values.sql = f"{base}.{values.name}"
        return values

    class Config:
        from_attributes = True


class DatabaseTable(BaseModel):
    fields: List[DatabaseField]
    type: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def push_order(cls, values):
        """ push order to children 
            order of the fields from the parent table
            is used to order the children fields
        """
        if values.get("fields") is not None:
            fields = []
            for i, field in enumerate(values.get("fields")):
                field["order"] = i
                fields.append(field)
            values["fields"] = fields
        return values

