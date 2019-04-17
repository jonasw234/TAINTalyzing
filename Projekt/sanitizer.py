# -*- coding: utf-8 -*-
"""A module to hold information about sanitizers."""
from __future__ import annotations


class Sanitizer:
    """Representation of a sink."""

    def __init__(self, definition: dict, level: int=0):
        """Constructor for class `Sink`.  Load definitions.

        Parameters
        ----------
        definition : dict
            Definitions for the object name, methods and sanitizers
        level : int, optional
            The depth of the nesting before the sanitizer is reached (sanitizers defined in the
            rules get a level of 0, sanitizers that call those get a level of 1, sanitizers that
            call those get a level of 2 and so on)
        """
        self.object_name = next(iter(definition))
        self.methods = definition[self.object_name]['Methods']
        self.level = level

# Make sure that the definition has a valid format
        assert all(['Methodname' in method for method in self.methods])
        assert all(['Parameters' in method for method in self.methods])
        assert all(['Comment' in method for method in self.methods])
