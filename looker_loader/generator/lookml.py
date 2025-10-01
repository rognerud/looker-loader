"""LookML Generator implementations."""

import os
from typing import Dict
from looker_loader.models.looker import LookerView, ValidatedLookerDimension, LookerMeasure
import logging


class LookmlGenerator:
    """
        Main LookML generator that coordinates dimension, view, and explore generation.
    """
    def __init__(self, cli_args):
        self._cli_args = cli_args

    def _dump_model(self, object, config):
        """ Handle dumping, with configurable options """
        if not config.include_descriptions:
            return object.model_dump(exclude={'description'})
        return object.model_dump()

    def _generate_views(self, model, config, views = None, parent = None):
        """Split up the model into views"""

        if views is None:
            views = []

        view_dimensions = []
        view_measures = []

        if parent is not None:
            view_name = f"{parent}__{model.name}{config.suffix_views}"
        else:
            view_name = f"{config.prefix_views}{model.name}{config.suffix_views}"

        for field in model.fields:
            view_dimensions.append(self._dump_model(field, config))

            if field.fields is not None:
                self._generate_views(field, config, views, parent=view_name)
            if field.measures is not None:
                for measure in field.measures:
                    view_measures.append(self._dump_model(measure, config))
        view = LookerView(**{
            "name": view_name,
            "sql_table_name": model.sql_table_name,
            "dimensions": view_dimensions,
            "measures": view_measures,
            "config": config
        })
        views.append(view)

        return views

    def _generate_joins(self, model, config, joins = None, parent = None, depth = 0):
        """Create a join for the model"""
        if joins is None:
            joins = []

        if parent is not None:
            parent_name = f"{parent}__{model.name}{config.suffix_views}"
        else:
            parent_name = f"{config.prefix_views}{model.name}{config.suffix_views}"

        for field in model.fields:
            if field.fields is not None:
                self._generate_joins(field, config, joins, parent=parent_name, depth=depth + 1)

        if parent is not None:
            join = {
                "name": parent_name,
                "sql": f"LEFT JOIN UNNEST(${{{parent}.{model.name}}}) AS {parent_name}",
                "type": "left_outer",
                "relationship": "one_to_many",
                "required_joins": [parent] if depth > 1 else None,
            }
            joins.append(join)

        return joins

    def _create_explore(self, model, config):
        """Create an explore for the model"""
        joins = self._generate_joins(model, config)

        if joins:
            explore = {
                "name": f"{config.prefix_views}{model.name}",
                "joins": joins,
                "hidden": "yes"
            }

            if config.explores_as_extensions:
                explore["extension"] = "required"

            return explore

    def generate(self, model, config) -> Dict:
        """Generate LookML for a model."""
        view_groups = self._generate_views(model, config)

        if config.explore:
            # Create joins and explore if explore is enabled
            explore = self._create_explore(model, config)
        else:
            explore = None

        return view_groups, explore