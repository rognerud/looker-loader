
from typing import Dict, Optional
from pydantic import BaseModel, Field, model_validator, field_validator, ValidationError, RootModel
from looker_loader.models.looker import (
    LookerDimension,
)

class Lex(RootModel):
    root: Dict[str, LookerDimension]

