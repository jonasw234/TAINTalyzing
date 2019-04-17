# -*- coding: utf-8 -*-
"""A module to hold information about sources."""
from __future__ import annotations


class Source:
    """Representation of a source."""

    def __init__(self, definition: dict):
        """Constructor for class `Source`.  Load definitions.

        Parameters
        ----------
        definition : dict
            Definitions for the object name and methods
            Example:
            {VulnObject: {'Methods': [{'Methodname': 'scanf', 'Parameters': [None, '$TAINT'],
                          'Comment': 'Reads formatted input from stdin'}]}}
        """
        self.object_name = next(iter(definition))
        self.methods = definition[self.object_name]['Methods']

        # Make sure that the definition has a valid format
        assert all(['Methodname' in method for method in self.methods])
        assert all(['Parameters' in method for method in self.methods])
        assert all(['Comment' in method for method in self.methods])
