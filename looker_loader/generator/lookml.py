"""LookML Generator implementations."""

import os
from typing import Dict



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
    
    def _generate_views(self, model, views = []):
        """Generate LookML for a view."""
        
        view_dimensions = []
        view_measures = []
        import logging
        logging.info(model)
        view_name = model.name

        for field in model.fields:
            view_dimensions.append(field)
            if field.measures is not None:
                for measure in field.measures:
                    view_measures.append(measure)

            if field.fields is not None:
                self._generate_views(field, views)

        view = {
            "name": view_name,
            "dimensions": view_dimensions,
            "measures": view_measures
        }
        views.append(view)

        return views

    def generate(self, model) -> Dict:
        """Generate LookML for a model."""
        
        views = self._generate_views(model)

        for view in views:
            