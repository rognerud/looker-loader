from pydantic import BaseModel, model_validator, Field
from typing import List, Optional, Dict
from looker_loader.enums import (
    LookerType,
    LookerBigQueryDataType
)
# Models for database information loading

class DatabaseField(BaseModel):
    name: str = Field(..., description="The name of the database field (e.g., 'user_id').")
    type: LookerType = Field(..., description="The Looker data type of the field (e.g., 'string', 'number', 'date').")
    db_type: str = Field(..., description="The underlying database data type (e.g., 'VARCHAR', 'INT', 'DATE').")
    order: int = Field(..., description="The ordinal position of the field within its parent structure.")
    mode: Optional[str] = Field(None, description="The nullable mode of the field (e.g., 'NULLABLE', 'REQUIRED').")
    is_clustered: Optional[bool] = Field(False, description="True if this field is used for clustering in the database.")
    description: Optional[str] = Field(None, description="A detailed textual description of the field's purpose or content.")
    parent_name: Optional[str] = Field(None, description="The name of the parent field if this is a nested field.")
    parent_mode: Optional[str] = Field(None, description="The mode of the parent field.")
    parent_type: Optional[str] = Field(None, description="The type of the parent field.")
    parent_db_type: Optional[str] = Field(None, description="The database type of the parent field.")
    is_nested: Optional[bool] = Field(False, description="True if this field is part of a nested structure.")
    depth: Optional[int] = Field(0, description="The nesting level of the field, starting from 0 for top-level.")
    sql: Optional[str] = Field(None, description="The SQL expression used to define this field, if applicable.")
    fields: Optional[List["DatabaseField"]] = Field(None, description="A list of child fields if this field is a record/struct type.")
    table_name: Optional[str] = Field(None, description="The name of the table this field belongs to.")
    sub_table_name: Optional[str] = Field(None, description="The name of the sub-table if this field is from a sub-table, else the table name.")


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
            copy["depth"] = values.get("depth", 0) + 1
            copy["sub_table_name"] = f"{values.get('table_name')}__{values.get('name')}"
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
                child["depth"] = values.get("depth", 0) + 1
                child["table_name"] = values.get("table_name")

                if hasattr(values, "parent_name"):
                    child["parent_name"] = f"{values.get('parent_name')}.{values.get('name')}"
                else:
                    child["parent_name"] = values.get("name")

                child["sub_table_name"] = f"{values.get('sub_table_name')}__{values.get("name")}"

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
                field["is_nested"] = True
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
                field["table_name"] = values.get("name")
                field["sub_table_name"] = values.get("name")
                ordered_fields.append(field)
            values["fields"] = ordered_fields

        return values
