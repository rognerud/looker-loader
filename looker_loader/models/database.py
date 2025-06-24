from pydantic import BaseModel, model_validator
from typing import List, Optional, Dict
from looker_loader.enums import (
    LookerType,
    LookerBigQueryDataType
)
# Models for database information loading

class DatabaseField(BaseModel):
    name: str
    type: LookerType
    db_type: str
    order: int
    mode: Optional[str] = None
    description: Optional[str] = None
    parent_name: Optional[str] = None
    parent_mode: Optional[str] = None
    parent_type: Optional[str] = None
    parent_db_type: Optional[str] = None
    sql: Optional[str] = None
    fields: Optional[List["DatabaseField"]] = None

    @model_validator(mode="before")
    def adjust_type(cls, values):
        """Adjust the type of the field based on the db_type."""
        db_type = values.get("type")
        type = LookerBigQueryDataType.get(db_type.upper())
        if type is None:
            raise ValueError(f"Invalid type: {db_type}")
        values["type"] = type
        values["db_type"] = db_type.upper()
        return values

    @model_validator(mode="before")
    def push_down_copy_for_repeated(cls, values):
        """ push down copy for repeated fields that are arrays """
        if values.get("mode") == "REPEATED" and values.get("fields") is None:
            copy = values.copy()
            copy["mode"] = "NULLABLE"
            copy["parent_db_type"] = "ARRAY"
            copy["parent_mode"] = "REPEATED"
            copy["description"] = f"A single value from {values.get("description", "")}"
            values["fields"] = [copy]
        return values

    @model_validator(mode="before")
    def push_down_attributes(cls, values):
        """ push parent_name, parent_mode and parent_type to children """
        if values.get("fields") is not None:
            inherited_children = []
            for child in values.get("fields"):
                child["parent_mode"] = values.get("mode")
                child["parent_type"] = values.get("type")
                child["parent_db_type"] = values.get("db_type")
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
        if values.parent_mode == "REPEATED" and values.parent_db_type == "ARRAY":
            values.sql = base
        else:
            values.sql = f"{base}.{values.name}"
        return values

    class Config:
        from_attributes = True


class DatabaseTable(BaseModel):
    name: str
    fields: List[DatabaseField]
    type: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    sql_table_name: Optional[str] = None

    table_group: Optional[str] = None
    table_project: Optional[str] = None

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    def flatten_non_repeated_structs(cls, values):
        """ flatten non-repeated structs that are not arrays """
        
        if values.get("fields") is not None:
            flattened_fields = []
            pop_fields = []

            for i, field in enumerate(values.get("fields")):
                struct_fields = []
                if field.get("mode") != "REPEATED" and field.get("type") == "RECORD" and field.get("fields") is not None:
                    # Flatten the struct
                    for subfield in field.get("fields"):
                        subfield["name"] = f"{field.get('name')}.{subfield.get('name')}"
                        struct_fields.append(subfield)

                    pop_fields.append(i)
                    flattened_fields.extend(struct_fields)

            if flattened_fields:
                for i in sorted(pop_fields, reverse=True):
                    values["fields"].pop(i)
                values["fields"].extend(flattened_fields)

            ordered_fields = []
            for i, field in enumerate(values.get("fields")):
                field["order"] = i
                ordered_fields.append(field)
            values["fields"] = ordered_fields

        return values
