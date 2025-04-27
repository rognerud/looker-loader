"""LookML Generator implementations."""

import os
from typing import Dict
from looker_loader.models.looker import LookerView, ValidatedLookerDimension, LookerMeasure



class LookmlGenerator:
    """Main LookML generator that coordinates dimension, view, and explore generation.
    
    This should be able to parse a list of models and generate LookML for each model.
    It should also be able to handle the generation of multiple views and explores.
    It should be able to handle nested views
    and generate the appropriate LookML for each view and explore.
    
    Should it do the following?
        parse the MixtureModels into LookerModels? (probably)

    """
    def __init__(self, cli_args):
        self._cli_args = cli_args
    
    def _generate_views(self, model, views = None, parent = None):
        """Split up the model into views"""

        if views is None:
            views = []
        view_dimensions = []
        view_measures = []

        if parent is not None:
            view_name = f"{parent}__{model.name}"
        else:
            view_name = model.name

        for field in model.fields:
            view_dimensions.append(field.model_dump())

            if field.fields is not None:
                self._generate_views(field, views, parent=view_name)
            if field.measures is not None:
                for measure in field.measures:
                    view_measures.append(measure.model_dump())
        view = LookerView(**{
            "name": view_name,
            "sql_table_name": model.sql_table_name,
            "dimensions": view_dimensions,
            "measures": view_measures,
        })
        views.append(view)

        return views

    def _create_explore(self, model):
        """Create an explore for the model"""
        explore = {
            "name": model.name,
            "joins": []
        }
        return explore
    

    def generate(self, model) -> Dict:
        """Generate LookML for a model."""
        
        view_groups = self._generate_views(model)

        return view_groups