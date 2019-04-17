# -*- coding: utf-8 -*-
"""A module to hold information about sinks."""
from __future__ import annotations
import copy

from sanitizer import Sanitizer


class Sink:
    """Representation of a sink."""

    def __init__(self, definition: dict):
        """Constructor for class `Sink`.  Load definitions.

        Parameters
        ----------
        definition : dict
            Definitions for the object name, methods and sanitizers
        """
        self.object_name = next(iter(definition))
        self.methods = definition[self.object_name]['Methods']
        for idx, method in enumerate(self.methods):
            original_sanitizers = copy.deepcopy(self.methods[idx].get('Sanitizers', []))
            method['Sanitizers'] = list()
            for sanitizer in original_sanitizers:
                method['Sanitizers'].append(Sanitizer(sanitizer))

        # Make sure that the definition has a valid format
        assert all(['Methodname' in method for method in self.methods])
        assert all(['Parameters' in method for method in self.methods])
        assert all(['Comment' in method for method in self.methods])
