# -*- coding: utf-8 -*-
"""Grammar definition for PHP files."""
from __future__ import annotations
import logging
from collections import OrderedDict
from typing import Generator

from pyparsing import *

from ..abstract_grammar import AbstractGrammar


class Grammar(AbstractGrammar):
    """Grammar definition for PHP files."""
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
        self.attribute_separator = oneOf('-> ::')
        self.ident = Word(alphas + '_', alphanums + '_')
        self.ident = Combine(ZeroOrMore(self.ident + self.attribute_separator)('object_name*') +
                             self.ident('ident*'))
        self.variable = Combine('$' + self.ident)
        self.rvalue = Forward()
        self.func_call = Forward()
        self.operators = Suppress(oneOf('|| && or and xor | & ^ . + - * / % << >> === !== < <= >'
                                        '>='))
        self.expression = Group(self.rvalue + ZeroOrMore(self.operators + (self.rvalue) |
                                                         self.func_call))
        self.expression |= Group(self.func_call + ZeroOrMore(self.operators + (self.rvalue |
                                                                               self.func_call)))

# Function calls
        self.param_list = Optional(delimitedList(Group(self.variable('parameter') | quotedString |
                                                       Word(nums) | self.func_call)))
        self.func_call << self.ident('name') + Suppress('(') + self.param_list('args') + \
            Suppress(')')

# Function body
        self.stmt = Forward()
        self.prototype = Forward()
        self.control_structures = Forward()
        self.func_body = Group(OneOrMore(Group(SkipTo(self.stmt | self.control_structures,
                                                      failOn=self.prototype, include=True))))

# Control structures -> increase edge count
        self.control_structures << (('else if' + '(' + self.expression + ')') |
                                    ('elseif' + '(' + self.expression + ')') |
                                    ('if' + '(' + self.expression + ')') |
                                    ('else') |
                                    ('case' + self.expression + ':') |
                                    ('default' + ':') |
                                    ('while' + '(' + self.expression + ')') |
                                    ('for' + '(' + Optional(self.expression) + ';' +
                                     Optional(self.expression) + ';' +
                                     Optional(self.expression) + ')') |
                                    ('foreach' + '(' + self.expression + 'as' + self.variable +
                                     Optional('=>' + self.variable) + ')') |
                                    ('goto' + self.ident))('control_structure')
# Mutually exclusive combinations: else if-else if, else if-else, else if, if-else if, if-else, if,
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

# Assignments
        self.assignment = self.variable('lvalue') + Suppress('=') + \
            Optional(Suppress('new')) + self.expression('expression')

# Return
        self.return_ = Suppress('return') + self.rvalue('return_value')

# Statements
        self.stmt << (self.func_call('func_call') | self.assignment('assignment') |
                      self.return_('return')) + Suppress(';')
        self.rvalue << (self.func_call | self.variable | Word(nums) | quotedString)

# Function definitions
        self.arg_list = Optional(delimitedList(Group(self.variable('name') +
                                                     Optional(Suppress('=') +
                                                              self.expression)('default_value'))))
        self.prototype << Suppress('function') + self.ident('name') + Suppress('(') + \
            self.arg_list('args') + Suppress(')')
        self.func_def = self.prototype + Suppress('{') + self.func_body('body') + Suppress('}')
        self.func_def.ignore(cppStyleComment | pythonStyleComment)

# Class definitions
        self.class_def = Suppress('class') + Word(alphas + '_', alphanums + '_') + \
            Optional(Suppress('extends' + Word(alphas + '_', alphanums + '_'))) + '{'

    def get_class_definitions(self) -> dict:
        """Return a dict of all class definitions with their start column.

        Returns
        -------
        dict
            A dict in the form of ClassName: start
        """
        classes = self.class_def.scanString(self.file_contents)
        classes_dict = OrderedDict()
        for class_ in classes:
            classes_dict[class_[0][0]] = class_[1]
        return classes_dict

    def get_self_identifier(self) -> str:
        """Returns the keyword that is used to reference the current object.

        Returns
        -------
        str
            The keyword to reference the current object (e.g. this or self)
        """
        return 'this'

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
                try:
                    parameters[parameter['name']] = parameter['default_value'][0][0]
                except KeyError:
                    parameters[parameter['name']] = None
            return parameters
        except ParseException:
            Grammar.logger.error('Tried to parse parameters in "{file}", but no match at start '
                                 'column {start}.', file=self.file_.path, start=start)

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
