# -*- coding: utf-8 -*-
"""Grammar definition for C files."""
from __future__ import annotations
import logging
from typing import Generator

from pyparsing import *

from ..abstract_grammar import AbstractGrammar


class Grammar(AbstractGrammar):
    """Grammar definition for C files."""
    logger = logging.getLogger('taintalyzing')

    def __init__(self, file_):
        """Constructor for a grammar object.

        Parameters
        ----------
        file_ : InputFile
            The file to parse
        """
        super().__init__(file_)
        ParserElement.enablePackrat()

# Helpers
        self.attribute_separator = oneOf('. ->')
        self.ident = Word(alphas, alphanums + '_')
        self.ident = Combine(ZeroOrMore(self.ident + self.attribute_separator)('object_name*') +
                             self.ident('ident*'))
        self.vartype = Suppress(Combine(Optional(oneOf('signed unsigned')) + self.ident +
                                        Optional(Word('*')), adjacent=False))
        self.array_index = '[' + Word(nums) + ']'
        self.rvalue = Forward()
        self.func_call = Forward()
        self.operators = Suppress(oneOf('|| && | & ^ . -> + - * / % << >> == != < <= > >='))
        self.expression = Group(self.rvalue + ZeroOrMore(self.operators + self.rvalue |
                                                         self.func_call))
        self.expression |= Group(self.func_call + ZeroOrMore(self.operators + (self.rvalue |
                                                                               self.func_call)))
        self.stmt = Forward()

# Function calls
        self.param_list = Optional(delimitedList(self.expression))
        self.func_call << self.ident('name') + Suppress('(') + self.param_list('args') + \
            Suppress(')')

# Control structures -> increase edge count
        self.control_structures = ((Keyword('case') + self.expression + ':') |
                                   (Keyword('default') + ':') |
                                   (Keyword('while') + '(' + self.expression + ')') |
                                   (Keyword('for') + '(' + Optional(self.expression) + ';' +
                                    Optional(self.expression) + ';' +
                                    Optional(self.expression) + ')') |
                                   (Keyword('goto') + self.ident))('control_structure')
# Mutually exclusive combinations: else if-else if, else if-else, else-if, if-else if, if-else, if,
# else
        self.mutually_exclusive_helper_expr = Suppress('(') + self.expression + Suppress(')')
        self.mutually_exclusive_helper_body = Suppress('{') + ZeroOrMore(self.stmt) + Suppress('}')
        self.mutually_exclusive_helper_body |= self.stmt
        self.mutually_exclusive = (Keyword('else if') + self.mutually_exclusive_helper_expr +
                                   self.mutually_exclusive_helper_body + FollowedBy(
                                       Keyword('else if') + self.mutually_exclusive_helper_expr +
                                       self.mutually_exclusive_helper_body))('alternative')
        self.mutually_exclusive |= (Keyword('else if') + self.mutually_exclusive_helper_expr +
                                    self.mutually_exclusive_helper_body + FollowedBy(
                                        Keyword('else') +
                                        self.mutually_exclusive_helper_body))('alternative')
        self.mutually_exclusive |= (Keyword('else if') + self.mutually_exclusive_helper_expr +
                                    self.mutually_exclusive_helper_body)('alternative')
        self.mutually_exclusive |= (Keyword('if') + self.mutually_exclusive_helper_expr +
                                    self.mutually_exclusive_helper_body + FollowedBy(
                                        Keyword('else if') + self.mutually_exclusive_helper_expr +
                                        self.mutually_exclusive_helper_body))
        self.mutually_exclusive |= (Keyword('if') + self.mutually_exclusive_helper_expr +
                                    self.mutually_exclusive_helper_body + FollowedBy(
                                        Keyword('else') + self.mutually_exclusive_helper_body))
        self.mutually_exclusive |= (Keyword('if') + self.mutually_exclusive_helper_expr +
                                    self.mutually_exclusive_helper_body)
        self.mutually_exclusive |= (Keyword('else') +
                                    self.mutually_exclusive_helper_body)('alternative-end')

# Function body
        self.prototype = Forward()
        self.func_body = Group(OneOrMore(Group(SkipTo(self.stmt | self.control_structures,
                                                      failOn=self.prototype, include=True))))

# Assignments
        self.assignment = self.ident('lvalue') + Optional(self.array_index) + \
            Suppress(oneOf('= -= += ^= &= |= *= %= /=')) + self.expression('expression')
        self.assignment |= self.vartype + self.assignment

# Return
        self.return_ = Suppress(Keyword('return')) + self.rvalue('return_value')

# Statements
        self.stmt << (self.func_call('func_call') | self.assignment('assignment') |
                      self.return_('return')) + Suppress(';')
        self.rvalue << (self.func_call | self.ident + Optional(self.array_index) | Word(nums) |
                        quotedString)

# Function definitions
        self.arg_list = Optional(delimitedList(Group(self.vartype + self.ident('name') +
                                                     Suppress(ZeroOrMore('[]')))))
        self.prototype << self.vartype('type') + self.ident('name') + Suppress('(') + \
            self.arg_list('args') + Suppress(')')
        self.func_def = self.prototype + Suppress('{') + self.func_body('body') + Suppress('}')
        self.func_def.ignore(cppStyleComment)

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
        return len(list(self.control_structures.scanString(self.file_contents[start:end]))) + \
            len(list(self.mutually_exclusive.scanString(self.file_contents[start:end]))) + \
            len(list(self.stmt.scanString(self.file_contents[start:end])))

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
        # Loops have three edges: Going into the loop, skipping the loop and returning from the last
        # position in the loop to the start of the loop
        # Mutually exclusive blocks have two edges, entering or not entering them
        return len(list(self.control_structures.scanString(self.file_contents[start:end]))) * 3 + \
            len(list(self.mutually_exclusive.scanString(self.file_contents[start:end]))) * 2 + \
            len(list(self.stmt.scanString(self.file_contents[start:end])))

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
        return self.mutually_exclusive.scanString(self.file_contents[start:end])

    def get_method_definitions(self) -> Generator[list, None, None]:
        """Return a generator for all methods with their bodies.

        Returns
        -------
        Generator
            Generator for all function definitions with their bodies
        """
        return self.func_def.scanString(self.file_contents)

    def get_method_calls(self, start, end) -> Generator[list, None, None]:
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
        return self.func_call.scanString(self.file_contents[start:end])

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
        try:
            args = self.prototype.parseString(self.file_contents[start:end]).get('args', [])
            parameters = dict()
            for parameter in args:
                parameters[parameter['name']] = None  # There are no default values in C
            return parameters
        except ParseException:
            Grammar.logger.error('Tried to parse parameters in "{file}", but no match at start '
                                 'column {start}.', file=self.file_.path, start=start)

    def get_declarations(self, start: int, end: int) -> Generator[list, None, None]:
        """Return a generator for variable declarations between `start` and `end`.

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
        declarations = Suppress(self.ident) + self.ident + Suppress(Optional(self.array_index)) + \
            Suppress(';')
        return declarations.scanString(self.file_contents[start:end])

    def get_global_variables(self) -> list:
        """Return a list of all global variables.

        Returns
        -------
        list
            List of all global variables
        """
        # First step: Find all the functions
        func_defs = self.get_method_definitions()
        func_defs_positions = [(function[1], function[2]) for function in func_defs]
        # Second step: Globals are by definition outside of functions
        start = -1
        outside_func_defs = []
        for position in func_defs_positions:
            outside_func_defs.append([start + 1, position[0] - 1 if position[0] > 0 else 0])
            start = position[1]
        if start + 1 <= len(self.file_contents):
            outside_func_defs.append([start + 1, len(self.file_contents)])
        # Third step: Find declarations and assignments in these regions
        globals_ = list()
        for start, end in outside_func_defs:
            assignments = list(self.get_assignments(start, end))
            assignments = [assignment[0] for assignment in assignments]
            globals_.extend(assignments)
            globals_.extend(list(self.get_declarations(start, end)))
        return globals_

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
        return self.assignment.scanString(self.file_contents[start:end])

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
        return self.control_structures.scanString(self.file_contents[start:end])

    def get_returns(self, start, end) -> Generator[list, None, None]:
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
        return self.return_.scanString(self.file_contents[start:end])
