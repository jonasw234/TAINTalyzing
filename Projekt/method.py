# -*- coding: utf-8 -*-
"""A module to hold information about methods."""
from __future__ import annotations


class Method:
    """Representation of a method."""

    def __init__(self, start: int, end: int, method_name: str, parameters: dict = None):
        """Constructor for class `Method`.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column
        method_name : str
            Name of the method
        parameters : dict
            Dictionary of all parameters and their default values
        """
        self.start = start
        self.end = end
        self.method_name = method_name
        self.parameters = parameters if parameters else dict()
        self.calls = dict()
        self.sources = dict()
        self.sanitizers = dict()
        self.sinks = dict()
        self.taints = dict()
        self.variables = dict()
        self.paths = list()
        self.complexity = -1

    def __add_new(self, original: dict, from_: dict):
        """Add new elements to `original` while avoiding duplicates.

        Parameters
        ----------
        original : dict
            The original dict to be updated
        from_ : dict
            Dict that stores the new elements
        """
        for element, uses in from_.items():
            if not original.get(element):
                original[element] = uses
            else:
                for use in uses:
                    if use not in original[element]:
                        original[element].append(use)

    def add_sources(self, sources: dict):
        """Add sources for this method.

        Parameters
        ----------
        sources : dict
            A dict of sources to be added in the form of source: call
        """
        self.__add_new(self.sources, sources)

    def add_sanitizers(self, sanitizers: dict):
        """Add sanitizers for this method.

        Parameters
        ----------
        sanitizers : dict
            A dict of sanitizers to be added in the form of sanitizer: call
        """
        self.__add_new(self.sanitizers, sanitizers)

    def add_sinks(self, sinks: dict):
        """Add sinks for this method.

        Parameters
        ----------
        sinks : dict
            A dict of sinks to be added in the form of sink: call
        """
        self.__add_new(self.sinks, sinks)

    def add_taints(self, taints: dict):
        """Add taints for this method.

        Parameters
        ----------
        taints : dict
            A dict of taints to be added in the form of taints: call
        """
        self.__add_new(self.taints, taints)

    def add_variables(self, variables: dict):
        """Add variables for this method.

        Parameters
        ----------
        variables : dict
            A dict of variables to be added in the form of variable: [calls]
        """
        self.__add_new(self.variables, variables)
