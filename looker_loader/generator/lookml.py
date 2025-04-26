"""LookML Generator implementations."""

import os
from typing import Dict
from looker_loader.models.looker import Looker, LookerDim



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
    
    def _generate_views(self, model, views = [], parent=None):
        """Split up the model into views"""
        
        view_dimensions = []
        view_measures = []

        if parent is not None:
            view_name = f"{parent}__{model.name}"
        else:
            view_name = model.name

        for field in model.fields:
            view_dimensions.append(field)

            if field.fields is not None:
                self._generate_views(field, views, parent=view_name)

        view = Looker(**{
            "name": view_name,
            "fields": view_dimensions,
        })
        views.append(view)

        return views

    def _extract_dimensions(self, model):
        """Extract dimensions from the model"""
        dimensions = []

        import logging
        logging.info(model)

        for field in model.fields:
            dimensions.append(field.model_dump())
            
        return dimensions

    def _extract_measures(self, model):
        """Extract measures from the model"""
        measures = []
        for field in model.fields:
            if field.measures is not None:
                for measure in field.measures:
                    measures.append(measure.model_dump())
        return measures

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

        # explore = self._create_explore(model)

        views = []
        # for view in views:
        for view in view_groups:
            view_name = view.name
            dimensions = self._extract_dimensions(view)
            measures = self._extract_measures(view)

            # Generate LookML for the view
            lookml_view = {
                "view": {
                    "name": view_name,
                    "dimensions": dimensions,
                    "measures": measures
                }
            }

            views.append(lookml_view)
        
        return views