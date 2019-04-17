# -*- coding: utf-8 -*-
"""A module to outline how grammar files should look for TAINTalyzing."""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Generator

from input_file import InputFile


class AbstractGrammar(ABC):
    """Abstract base class for grammar definitions."""

    def __init__(self, file_: InputFile):
        """Constructor for a grammar object.

        Parameters
        ----------
        file_ : InputFile
            The file to parse
        """
        self.file_ = file_
        self.file_contents = file_.read_file()
        super().__init__()

    def get_class_definitions(self) -> OrderedDict:
        """Return an ordered dict of all class definitions with their start column.
        Override if needed.

        Returns
        -------
        OrderedDict
            An ordered dict in the form of ClassName: start
        """
        return OrderedDict()

    def get_self_identifier(self) -> str:
        """Returns the keyword that is used to reference the current object.
        Override if needed.

        Returns
        -------
        str
            The keyword to reference the current object (e.g. this or self)
        """
        return ''

    @abstractmethod
    def get_statement_count(self, start: int, end: int) -> int:
        """Return the number of statements between `start` and `end`.

        Statements are all lines that have an actual effect on the program flow, e.g. method calls
        or loops.

        Parameters
        ----------
        start : int
            The start column
        end : int
            The end column

        Returns
        -------
        int
            The number of statements between `start` and `end`.
        """
        pass

    @abstractmethod
    def get_edge_count(self, start: int, end: int) -> int:
        """Return the edge count between `start` and `end`.

        Edges are all statements that can branch into two paths, e.g. loops, conditions etc.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column

        Returns
        -------
        int
            The edge count between `start` and `end`.
        """
        pass

    @abstractmethod
    def get_mutually_exclusive_positions(self, start: int, end: int) -> Generator[list, None, None]:
        """Return a generator for all mutually exclusive positions from `start` to `end`.
        That is return the start and end position for all the statements where a mutually exclusive
        block begins and where it ends.

        Parameters
        ----------
        start : int
            The start column
        end : int
            The end column

        Returns
        -------
        Generator
            Generator for all mutually exclusive paths from `start` to `end`.
        """
        pass

    @abstractmethod
    def get_method_definitions(self) -> Generator[list, None, None]:
        """Return a generator for all methods with their bodies.

        Returns
        -------
        Generator
            Generator for all function definitions with their bodies
        """
        pass

    @abstractmethod
    def get_method_calls(self, start: int, end: int) -> Generator[list, None, None]:
        """Return a generator for all function calls between `start` and `end`.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column

        Returns
        -------
        Generator
            Generator for all function calls
        """
        pass

    @abstractmethod
    def get_parameters(self, start: int, end: int) -> dict:
        """Return a dictionary of all parameters between `start` and `end` with their default value.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column

        Returns
        -------
        dict
            Dictionary with parameter: default value
        """
        pass

    def get_declarations(self, start: int, end: int) -> Generator[list, None, None]:
        """Return a generator for variable declarations between `start` and `end`.
        Override if needed.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column

        Returns
        -------
        Generator
            Generator for all declarations
        """
        yield from()

    def get_global_variables(self) -> list:
        """Return a list of all global variables.
        Override if needed.

        Returns
        -------
        list
            List of all global variables
        """
        pass

    @abstractmethod
    def get_assignments(self, start: int, end: int) -> Generator[list, None, None]:
        """Return a generator for all assignments betweeen `start` and `end`.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column

        Returns
        -------
        Generator
            Generator for all assignments
        """
        pass

    @abstractmethod
    def get_control_structures(self, start: int, end: int) -> Generator[list, None, None]:
        """Return a generator for all control structures between `start` and `end`.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column

        Returns
        -------
        Generator
            Generator for all control structures
        """
        pass

    @abstractmethod
    def get_returns(self, start: int, end: int) -> Generator[list, None, None]:
        """Return a generator for all return values between `start` and `end`.

        Parameters
        ----------
        start : int
            Start column
        end : int
            End column

        Returns
        -------
        Generator
            Generator for all return values
        """
        pass
