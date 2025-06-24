
from typing import Dict, Optional
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError, RootModel
from looker_loader.models.looker import (
    LookerDimension,
)

class Lex(RootModel):
    root: Dict[str, LookerDimension]

    @model_validator(mode="before")
    def remove_null_labels(cls, values):
        cleaned = {
            k: v for k, v in values.items()
            if v.get("label") is not None
        }
        for k, v in cleaned.items():
            v["name"] = k
        return cleaned