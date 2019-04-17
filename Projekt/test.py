#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module provides unit tests for the TAINTalyzing framework."""
from __future__ import annotations
from copy import copy
import logging
import os
import unittest

from main import find_files
from analysis import Analysis
from input_file import InputFile
from ruleset import Ruleset
from modules.c.grammar import Grammar as CGrammar
from modules.php.grammar import Grammar as PHPGrammar
from modules.python.grammar import Grammar as PythonGrammar
from method import Method
from sink import Sink
from source import Source


def replace_sink_rules(ruleset: Ruleset, new_rules: list):
    """Replace existing sink rules from a ruleset with `new_rules`.

    Parameters
    ----------
    ruleset : Ruleset
        Replace the rules in this ruleset
    new_rules : dict
        New rules to replace the old ones.
    """
    ruleset.sinks = []
    for rule in new_rules:
        sink_ = Sink(rule)
        ruleset.sinks.append(sink_)


def replace_source_rules(ruleset: Ruleset, new_rules: list):
    """Replace existing source rules from a ruleset with `new_rules`.

    Parameters
    ----------
    ruleset : Ruleset
        Replace the rules in this ruleset
    new_rules : dict
        New rules to replace the old ones.
    """
    ruleset.sources = []
    for rule in new_rules:
        source_ = Source(rule)
        ruleset.sources.append(source_)


class TestMain(unittest.TestCase):
    """Test cases for main module."""
    def test_find_files(self):
        """Check if all files are found."""
        should_find = [os.sep.join(['testfiles', 'main', 'binary-file.odt']),
                       os.sep.join(['testfiles', 'main', 'unix.txt']),
                       os.sep.join(['testfiles', 'main', 'exclude-subdirectory',
                                    'binary-file.odt']),
                       os.sep.join(['testfiles', 'main', 'exclude-subdirectory',
                                    'excluded-file.txt']),
                       os.sep.join(['testfiles', 'main', 'exclude-subdirectory', 'excluded-dir',
                                    'excluded-subdir-file']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'binary-file.odt']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'dos.txt']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'file.swp']),
                       ]
        self.assertListEqual(should_find, list(find_files(os.sep.join(['testfiles', 'main']))))

    def test_find_files_exclude(self):
        """Test if single excludes work."""
        should_find = [os.sep.join(['testfiles', 'main', 'binary-file.odt']),
                       os.sep.join(['testfiles', 'main', 'unix.txt']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'binary-file.odt']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'dos.txt']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'file.swp']),
                       ]
        self.assertListEqual(should_find, list(find_files(os.sep.join(['testfiles', 'main']),
                                                          exclude=['exclude-subdirectory'])))

    def test_find_files_multiple_excludes(self):
        """Test if multiple excludes work independently from each other."""
        should_find = [os.sep.join(['testfiles', 'main', 'binary-file.odt']),
                       os.sep.join(['testfiles', 'main', 'unix.txt']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'binary-file.odt']),
                       os.sep.join(['testfiles', 'main', 'subdirectory', 'dos.txt']),
                       ]
        self.assertListEqual(should_find, list(find_files(os.sep.join(['testfiles', 'main']),
                                                          exclude=['exclude-subdirectory',
                                                                   r'\.swp$'])))

    def test_find_files_exclude_all(self):
        """Test if no error is thrown if everything is excluded."""
        should_find = []
        self.assertListEqual(should_find, list(find_files(os.sep.join(['testfiles', 'main']),
                                                          exclude=[''])))


class TestInputFile(unittest.TestCase):
    """Test cases for InputFile module."""
    def test_read_file_ascii_dos(self):
        """Check if an ASCII file with DOS line endings can be read."""
        input_file = InputFile(os.sep.join(['testfiles', 'main', 'subdirectory', 'dos.txt']))
        self.assertEqual('file contents!\n', input_file.read_file())

    def test_read_file_ascii_utf8_unix(self):
        """Check if an ASCII, utf8 encoded file with Unix line endings can be read."""
        input_file = InputFile(os.sep.join(['testfiles', 'main', 'unix.txt']))
        self.assertEqual('file with unix line endings\n', input_file.read_file())

    def test_read_binary_file(self):
        """Make sure binary files are handled gracefully."""
        input_file = InputFile(os.sep.join(['testfiles', 'main', 'binary-file.odt']))
        try:
            input_file.read_file()
        except:
            self.fail()

    def test_extension_detection(self):
        """Make sure files can be detected based on extension alone."""
        input_file = InputFile(os.sep.join(['testfiles', 'filetype_detection', 'empty.cpp']))
        input_file.detect_filetype()
        self.assertEqual(input_file.module, 'cpp')

    def test_magic_detection(self):
        """Make sure files can be detected based on the magic number."""
        input_file = InputFile(os.sep.join(['testfiles', 'filetype_detection', 'python-magic.py']))
        input_file.detect_filetype()
        self.assertEqual(input_file.module, 'python')

    def test_multiple_magic_detection(self):
        """Make sure files can be correctly detected even if multiple magic numbers match."""
        # C++ files are detected as C files, so multiple matches, but single match for file extension
        input_file = InputFile(os.sep.join(['testfiles', 'filetype_detection',
                                            'multiple-magic.cpp']))
        input_file.detect_filetype()
        self.assertEqual(input_file.module, 'cpp')

    def test_heuristic_detection(self):
        """Make sure heuristic correctly identifies files based on majority of recognized filetypes
        in the same directory."""
        input_file = InputFile(os.sep.join(['testfiles', 'filetype_detection', 'project-folder',
                                            'include_statement']))
        self.assertEqual(input_file.detect_heuristic(), 'c')

    def test_heuristic_detection_empty(self):
        """Make sure heuristic detection just returns an empty string when no modules can be
        identified for any of the files in the same directory.
        """
        input_file = InputFile(os.sep.join(['testfiles', 'filetype_detection', 'unknown-project',
                                            'include_statement']))
        self.assertEqual(input_file.detect_heuristic(), '')

    def test_heuristic_detection_respect_possibilities(self):
        """Make sure that the heuristic detection respect the list of possible detections from other
        detection methods.
        """
        input_file = InputFile(os.sep.join(['testfiles', 'filetype_detection', 'project-folder',
                                            'include_statement']))
        # Force invalid possibilities to check if heuristic detection overrides it
        self.assertEqual(input_file.detect_heuristic([('python', ['.py'], 'Python script')]), "")

    def test_fallback_detection(self):
        """Make sure fallback detection works if nothing else matches."""
        input_file = InputFile(os.sep.join(['testfiles', 'filetype_detection',
                                            'unknown_extension.python']), 'python')
        input_file.detect_filetype()
        self.assertEqual(input_file.module, 'python')


class TestCGrammar(unittest.TestCase):
    """Test cases for C grammar file for parsing C files."""

    def test_single_instruction(self):
        """Make sure files with a single instruction in the method body are parsed correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_single_instruction.c']))
        grammar = CGrammar(input_file)
        parsetree = next(grammar.get_method_definitions())
        self.assertEqual(parsetree[0]['name']['ident'][0], 'main')
        self.assertEqual(parsetree[0]['args'][0]['name']['ident'][0], 'argc')
        self.assertEqual(parsetree[0]['args'][1]['name']['ident'][0], 'argv')
        self.assertEqual(parsetree[0]['body'][0]['name']['ident'][0], 'printf')

    def test_multiple_instructions(self):
        """Make sure multiple instructions in the method body are parsed correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_multiple_instructions.c']))
        grammar = CGrammar(input_file)
        parsetree = next(grammar.get_method_definitions())
        for idx, method in enumerate(parsetree[0]['body']):
            self.assertEqual(method['name']['ident'][0], 'printf' if idx == 0 else 'add')

    def test_unknown_tokens(self):
        """Make sure unknown tokens don't confuse the parser."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_unknown_tokens.c']))
        grammar = CGrammar(input_file)
        parsetree = next(grammar.get_method_definitions())
        self.assertEqual(parsetree[0]['name']['ident'][0], 'main')
        self.assertEqual(parsetree[0]['body'][0]['name']['ident'][0], 'printf')
        self.assertEqual(parsetree[0]['body'][1]['lvalue']['ident'][0], 'i')
        self.assertEqual(len(parsetree[0]['body'][3]['args']), 3)
        self.assertEqual(parsetree[0]['body'][3]['name']['ident'][0], 'printf')

    def test_multiple_functions(self):
        """Make sure multiple functions are detected correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_multiple_functions.c']))
        grammar = CGrammar(input_file)
        definitions = grammar.get_method_definitions()
        parsetree_first_function = next(definitions)
        self.assertEqual(parsetree_first_function[0]['name']['ident'][0], 'add')
        self.assertEqual(parsetree_first_function[0]['body'][1]['return_value'], 'c')
        parsetree_second_function = next(definitions)
        self.assertEqual(parsetree_second_function[0]['body'][1]['name']['ident'][0], 'printf')
        self.assertEqual(len(parsetree_second_function[0]['body'][1]['args']), 2)

    def test_identify_returns(self):
        """Make sure multiple returns are detected correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_multiple_returns.c']))
        grammar = CGrammar(input_file)
        returns = grammar.get_returns(input_file.line_to_column(2), input_file.line_to_column(4))
        first_return = next(returns)
        self.assertEqual(first_return[0]['return_value'], '1')
        second_return = next(returns)
        self.assertEqual(second_return[0]['return_value'], '0')

    def test_assignments(self):
        """Make sure assignments are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_multiple_functions.c']))
        grammar = CGrammar(input_file)
        assignments = grammar.get_assignments(60, 166)
        first = next(assignments)
        self.assertEqual(first[0]['lvalue']['ident'][0], 'a')
        self.assertEqual(first[0]['expression'][0]['name']['ident'][0], 'add')
        self.assertEqual(first[0]['expression'][0]['args'][0][0], '2')
        self.assertEqual(first[0]['expression'][0]['args'][1][0], '3')
        second = next(assignments)
        self.assertEqual(second[0]['lvalue']['ident'][0], 'a')
        self.assertEqual(second[0]['expression'][0][0], '5')

    def test_follow_variables(self):
        """Make sure that variables are followed correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_multiple_functions.c']))
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        method = Method(60, 167, {'ident': ['main']})
        dataflow = analysis.follow_variables(method)
        for variable, flow in dataflow.items():
            if variable[1] == 'argc':
                self.assertListEqual(flow, [[{'ident': ['argc'], 'lvalue': ['argc'], 'expression':
                                              [{'name': {'ident': [None]}}]}, 0, 0]])
            elif variable[1] == 'argv':
                self.assertListEqual(flow, [[{'ident': ['argv'], 'lvalue': ['argv'], 'expression':
                                              [{'name': {'ident': [None]}}]}, 0, 0]])
            elif variable[1] == 'a':
                self.assertEqual(len(flow), 3)
                self.assertEqual(flow[1][0]['name']['ident'][0], 'printf')
            else:
                self.fail(f'Unknown variable: {variable[1]}')

    def test_detect_parameters(self):
        """Make sure parameters and default values are detected correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'c_single_instruction.c']))
        grammar = CGrammar(input_file)
        parameters = grammar.get_parameters(0, 64)
        for parameter, value in parameters.items():
            if parameter['ident'][0] == 'argc':
                self.assertEqual(value, None)
            elif parameter['ident'][0] == 'argv':
                self.assertEqual(value, None)
            else:
                self.fail('Unknown parameter.')


class TestPHPGrammar(unittest.TestCase):
    """Test cases for PHP grammar file for parsing PHP files."""

    def test_detect_parameters(self):
        """Make sure parameters and default values are detected correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'php_default_parameters.php']))
        grammar = PHPGrammar(input_file)
        parameters = grammar.get_parameters(6, 94)
        for parameter, value in parameters.items():
            if parameter['ident'][0] == 'typ':
                self.assertEqual(value, '"Cappuccino"')
            else:
                self.fail('Unknown parameter.')

    def test_multiple_instructions(self):
        """Make sure multiple instructions in the method body are parsed correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser',
                                            'php_multiple_instructions.php']))
        grammar = PHPGrammar(input_file)
        parsetree = next(grammar.get_method_definitions())
        self.assertEqual(parsetree[0]['name']['ident'][0], 'divideNumbers')
        self.assertEqual(len(parsetree[0]['args']), 2)
        self.assertEqual(parsetree[0]['args'][1]['name']['ident'][0], 'divisor')
        self.assertListEqual(parsetree[0]['body'][0]['expression'].asList(), [['$dividend',
                                                                               '$divisor']])
        self.assertEqual(parsetree[0]['body'][1]['lvalue']['ident'][0], 'array')

    def test_find_classes(self):
        """Make sure classes are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'php_detect_classes.php']))
        grammar = PHPGrammar(input_file)
        self.assertDictEqual(grammar.get_class_definitions(), {'MyClass': 6, 'MyOtherClass': 136})


class TestPythonGrammar(unittest.TestCase):
    """Test cases for Python grammar file for parsing Python files."""

    def test_detect_parameters(self):
        """Make sure parameters and default values are detected correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'python_default_parameters.py']))
        grammar = PythonGrammar(input_file)
        parameters = grammar.get_parameters(29, 73)
        for parameter, value in parameters.items():
            if parameter['ident'][0] == 'a':
                self.assertEqual(value, '5')
            else:
                self.fail('Unknown parameter')

    def test_multiple_instructions(self):
        """Make sure multiple instructions in the method body are parsed correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'python_multiple_functions.py']))
        grammar = PythonGrammar(input_file)
        defs = grammar.get_method_definitions()
        parsetree_first_function = next(defs)
        self.assertEqual(parsetree_first_function[0]['name']['ident'][0], 'test_function')
        self.assertEqual(parsetree_first_function[0]['body'][0][1]['name']['ident'][0], 'print')
        self.assertEqual(parsetree_first_function[0]['body'][0][3]['return_value'], "'a'")
        parsetree_second_function = next(defs)
        self.assertListEqual(parsetree_second_function[0]['body'][0][0]['args'][0][0].asList(),
                             ['a', 'b', 'c'])

    def test_find_classes(self):
        """Make sure classes are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'parser', 'python_detect_classes.py']))
        grammar = PythonGrammar(input_file)
        self.assertDictEqual(grammar.get_class_definitions(), {'ClassName': 48,
                                                               'Another_Class_Name': 113})


class TestRuleset(unittest.TestCase):
    """Test cases for rulesets."""

    def test_load_sinks(self):
        """Make sure that sinks are loaded successfully."""
        ruleset = Ruleset('c')
        sinks = ruleset.sinks
        for sink in sinks:
            methods = sink.methods
            for method in methods:
                if method['Methodname'] == 'strcpy':
                    self.assertListEqual(method['Parameters'], [None, '$TAINT'])
                    self.assertNotEqual(method['Comment'], '')
                    break

    def test_load_sanitizers(self):
        """Make sure that sanitizers are loaded successfully."""
        ruleset = Ruleset('c')
        replace_sink_rules(
            ruleset,
            [{None: {
                'Methods': [{'Methodname': 'printf',
                             'Parameters': ['$TAINT'],
                             'Comment': 'Format string vulnerability.',
                             'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                 'Parameters': [],
                                                                 'Comment': 'For testing purposes '
                                                                            'only.'},
                                                                {'Methodname': 'test2',
                                                                 'Parameters': [None],
                                                                 'Comment': 'For testing purposes '
                                                                            'only.'}]}}]}]}}])
        sinks = ruleset.sinks
        for sink in sinks:
            methods = sink.methods
            for method in methods:
                if method['Methodname'] == 'printf':
                    self.assertEqual(len(method['Sanitizers'][0].methods), 2)
                    self.assertEqual(method['Sanitizers'][0].methods[1]['Methodname'], 'test2')
                    break

    def test_load_sources(self):
        """Make sure that sources are loaded successfully."""
        ruleset = Ruleset('c')
        sources = ruleset.sources
        for source in sources:
            methods = source.methods
            for method in methods:
                if method['Methodname'] == 'scanf':
                    self.assertEqual(len(method['Parameters']), 2)
                    break


class TestAnalysis(unittest.TestCase):
    """Test cases for analyses."""

    def test_find_methods(self):
        """Make sure all methods are recognized correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'format-string.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            if method.method_name['ident'][0] == 'vuln':
                self.assertEqual(method.start, 20)
                self.assertEqual(method.end, 67)
            elif method.method_name['ident'][0] == 'main':
                self.assertEqual(method.start, 69)
                self.assertEqual(method.end, 283)
            else:
                self.fail('Unknown method found.')

    def test_find_variable_simple(self):
        """Make sure that simple variable sources are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'simple-source.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        method = Method(20, 286, {'ident': ['main']})
        analysis.follow_variables(method)
        trail = analysis.find_variable_source(method, None, 'userControlledToo', 202)
        self.assertEqual(len(trail), 4)
        self.assertEqual(trail[0][1], 38)
        self.assertEqual(trail[1][1], 105)
        self.assertEqual(trail[2][1], 138)
        self.assertEqual(trail[3][1], 202)

    def test_find_variable_source(self):
        """Make sure that variable sources over multiple functions are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis',
                                            'variable-source-multiple-functions.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        method = Method(20, 114, {'ident': ['vuln']})
        analysis.follow_variables(method)
        trail = analysis.find_variable_source(method, None, 'userInputUsed', 93)
        self.assertEqual(len(trail), 3)
        self.assertEqual(trail[0][1], 0)
        self.assertEqual(trail[1][1], 34)
        self.assertEqual(trail[2][1], 72)

    def test_find_sources(self):
        """Make sure that sources are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'format-string.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        replace_sink_rules(
            analysis.ruleset,
            [{None: {'Methods': [{'Methodname': 'printf',
                                  'Parameters': ['$TAINT'],
                                  'Comment': 'Format string vulnerability.',
                                  'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                      'Parameters': [],
                                                                      'Comment': 'For testing '
                                                                                 'purposes only.'},
                                                                     {'Methodname': 'test2',
                                                                      'Parameters': [None],
                                                                      'Comment': 'For testing '
                                                                                 'purposes '
                                                                                 'only.'}]}}]}]}}])
        sources = analysis.find_sources(Method(69, 283, {'ident': ['main']}))
        for source_, calls in sources.items():
            if source_.object_name is None:
                self.assertListEqual(source_.methods, [{'Methodname': 'scanf', 'Parameters':
                                                        [None, '$TAINT'], 'Comment':
                                                            'Reads formatted input from stdin'}])
                self.assertEqual(calls[0][0]['name']['ident'][0], 'scanf')
                self.assertEqual(calls[0][1], 105)
                self.assertEqual(calls[0][2], 132)
            else:
                self.fail('Unknown source found.')

    def test_find_sinks(self):
        """Make sure that sinks are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'format-string.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        replace_sink_rules(
            analysis.ruleset,
            [{None: {'Methods': [{'Methodname': 'printf',
                                  'Parameters': ['$TAINT'],
                                  'Comment': 'Format string vulnerability.',
                                  'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                      'Parameters': [],
                                                                      'Comment': 'For testing '
                                                                                 'purposes only.'},
                                                                     {'Methodname': 'test2',
                                                                      'Parameters': [None],
                                                                      'Comment': 'For testing '
                                                                                 'purposes '
                                                                                 'only.'}]}}]}]}}])
        sinks = analysis.find_sinks(Method(20, 67, {'ident': ['vuln']}))
        for sink_, calls in sinks.items():
            if sink_.object_name is None:
                for method in sink_.methods:
                    if method['Methodname'] == 'printf':
                        self.assertListEqual(method['Parameters'], ['$TAINT'])
                        self.assertEqual(calls[0][0]['name']['ident'][0], 'printf')
                        self.assertEqual(len(calls[0][0]['args']), 1)
                        self.assertEqual(calls[0][1], 30)
                        self.assertEqual(calls[0][2], 43)
                        continue
                    self.fail('Unknown sink found.')

    def test_find_sanitizers(self):
        """Make sure that sanitizers are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles' + os.sep + 'analysis' + os.sep +
                                            'sanitizer.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        replace_sink_rules(
            analysis.ruleset,
            [{None: {'Methods': [{'Methodname': 'printf',
                                  'Parameters': ['$TAINT'],
                                  'Comment': 'Format string vulnerability.',
                                  'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                      'Parameters': [],
                                                                      'Comment': 'For testing '
                                                                                 'purposes only.'},
                                                                     {'Methodname': 'test2',
                                                                      'Parameters': [None],
                                                                      'Comment': 'For testing '
                                                                                 'purposes '
                                                                                 'only.'}]}}]}]}}])
        method = Method(20, 79, {'ident': ['vuln']})
        analysis.find_sinks(method)
        sanitizers = analysis.find_sanitizers(method)
        for sanitizer_, calls in sanitizers.items():
            if sanitizer_.object_name is None:
                self.assertEqual(calls[0][0]['name']['ident'][0], 'test')
                self.assertEqual(calls[0][1], 30)
                self.assertEqual(calls[0][2], 36)

    def test_find_simple_taints(self):
        """Make sure taints are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'simple-taint.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        replace_sink_rules(
            analysis.ruleset,
            [{None: {'Methods': [{'Methodname': 'printf',
                                  'Parameters': ['$TAINT'],
                                  'Comment': 'Format string vulnerability.',
                                  'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                      'Parameters': [],
                                                                      'Comment': 'For testing '
                                                                                 'purposes only.'},
                                                                     {'Methodname': 'test2',
                                                                      'Parameters': [None],
                                                                      'Comment': 'For testing '
                                                                                 'purposes '
                                                                                 'only.'}]}}]}]}}])
        method = Method(20, 286, {'ident': ['main']})
        analysis.follow_variables(method)
        analysis.find_sources(method)
        analysis.find_sinks(method)
        analysis.find_sanitizers(method)
        analysis.find_taints(method)
        taints = method.taints
        self.assertEqual(len(taints), 1)
        for data in taints.values():
            self.assertEqual(data[0]['Comment'], 'Format string vulnerability.')
            self.assertEqual(data[0]['Position'], (205, 230))

    def test_find_sanitized_simple_taints(self):
        """Make sure that sanitized sinks are also identified as taints with a reference to the
        sanitizer.
        """
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'sanitized-taint.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        replace_sink_rules(
            analysis.ruleset,
            [{None: {'Methods': [{'Methodname': 'printf',
                                  'Parameters': ['$TAINT'],
                                  'Comment': 'Format string vulnerability.',
                                  'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                      'Parameters': [],
                                                                      'Comment': 'For testing '
                                                                                 'purposes only.'},
                                                                     {'Methodname': 'test2',
                                                                      'Parameters': [None],
                                                                      'Comment': 'For testing '
                                                                                 'purposes '
                                                                                 'only.'}]}}]}]}}])
        method = Method(20, 286, {'ident': ['main']})
        analysis.follow_variables(method)
        analysis.find_sources(method)
        analysis.find_sinks(method)
        analysis.find_sanitizers(method)
        analysis.find_taints(method)
        taints = method.taints
        self.assertEqual(len(taints), 1)
        for sinks in taints.values():
            self.assertEqual(sinks[0]['Sanitizer'].methods[0]['Methodname'], 'test')

    def test_follow_sanitizers(self):
        """Make sure that sanitizers are followed across method calls."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis',
                                            'follow-sanitizer-functions.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        replace_sink_rules(
            analysis.ruleset,
            [{None: {'Methods': [{'Methodname': 'printf',
                                  'Parameters': ['$TAINT'],
                                  'Comment': 'Format string vulnerability.',
                                  'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                      'Parameters': [],
                                                                      'Comment': 'For testing '
                                                                                 'purposes only.'},
                                                                     {'Methodname': 'test2',
                                                                      'Parameters': [None],
                                                                      'Comment': 'For testing '
                                                                                 'purposes '
                                                                                 'only.'}]}}]}]}}])
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        # Sanitizer should have been added and no unsanitized taints should remain
        self.assertEqual(len(analysis.methods[1].sanitizers), 1)
        for method in analysis.methods:
            if method.method_name['ident'][0] == 'sanitize':
                self.assertDictEqual(method.taints, {})
            else:
                self.assertEqual(len(method.taints), 1)
                for sinks in method.taints.values():
                    for sink in sinks:
                        self.assertNotEqual(sink.get('Sanitizer'), None)
                        self.assertEqual(sink['Sanitizer'].level, 1)

    def test_follow_sources_parameters(self):
        """Make sure that methods which have parameters that are used as arguments to sources are
        added as sources themselves.
        """
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'follow-source-functions.c']),
                               'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[1].taints), 1)

    def test_follow_sources_returns(self):
        """Make sure that methods which have returns based on sources are added as sources
        themselves.
        """
        input_file = InputFile(os.sep.join(['testfiles', 'analysis',
                                            'follow-source-functions-return.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[1].taints), 1)

    def test_follow_sources_direct_returns(self):
        """Make sure that methods which have returns based on sources are added as sources
        themselves.
        """
        input_file = InputFile(os.sep.join(['testfiles', 'analysis',
                                            'follow-source-functions-direct-return.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[1].taints), 1)

    def test_follow_taints(self):
        """Make sure that taints are followed across method calls."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'follow-taint-functions.c']),
                               'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        replace_sink_rules(
            analysis.ruleset,
            [{None: {'Methods': [{'Methodname': 'printf',
                                  'Parameters': ['$TAINT'],
                                  'Comment': 'Format string vulnerability.',
                                  'Sanitizers': [{None: {'Methods': [{'Methodname': 'test',
                                                                      'Parameters': [],
                                                                      'Comment': 'For testing '
                                                                                 'purposes only.'},
                                                                     {'Methodname': 'test2',
                                                                      'Parameters': [None],
                                                                      'Comment': 'For testing '
                                                                                 'purposes '
                                                                                 'only.'}]}}]}]}}])
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[1].taints), 1)

    def test_follow_taints_classes(self):
        """Make sure that taints are followed across classes."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'follow-taint-classes.php']),
                               'php')
        grammar = PHPGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('php'))
        replace_sink_rules(analysis.ruleset,
                           [{None: {
                               'Methods': [{'Methodname': 'eval',
                                            'Parameters': ['$TAINT'],
                                            'Comment': 'Arbitrary code execution.'}]}}])
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.fix_object_names(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[1].taints), 1)

    def test_exclusive_path(self):
        """Make sure a single exclusive path is recognized."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'exclusive-path.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.find_paths_through(method)
        self.assertListEqual(analysis.methods[0].paths, [
            [(20, 59), (59, 90), (220, 236)],
            [(20, 59), (90, 135), (220, 236)],
            [(20, 59), (135, 182), (220, 236)],
            [(20, 59), (182, 220), (220, 236)]])

    def test_exclusive_paths(self):
        """Make sure exclusive paths are recognized."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'exclusive-paths.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.find_paths_through(method)
        self.assertListEqual(analysis.methods[0].paths, [
            [(20, 59), (59, 89), (89, 126), (126, 164), (206, 252), (252, 283), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (126, 164), (206, 252), (283, 320), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (126, 164), (206, 252), (320, 357), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (126, 164), (206, 252), (357, 386), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (164, 206), (206, 252), (252, 283), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (164, 206), (206, 252), (283, 320), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (164, 206), (206, 252), (320, 357), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (164, 206), (206, 252), (357, 386), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (206, 206), (206, 252), (252, 283), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (206, 206), (206, 252), (283, 320), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (206, 206), (206, 252), (320, 357), (386, 403)],
            [(20, 59), (59, 89), (89, 126), (206, 206), (206, 252), (357, 386), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (126, 164), (206, 252), (252, 283), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (126, 164), (206, 252), (283, 320), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (126, 164), (206, 252), (320, 357), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (126, 164), (206, 252), (357, 386), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (164, 206), (206, 252), (252, 283), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (164, 206), (206, 252), (283, 320), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (164, 206), (206, 252), (320, 357), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (164, 206), (206, 252), (357, 386), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (206, 206), (206, 252), (252, 283), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (206, 206), (206, 252), (283, 320), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (206, 206), (206, 252), (320, 357), (386, 403)],
            [(20, 59), (89, 89), (89, 126), (206, 206), (206, 252), (357, 386), (386, 403)]])

    def test_mutually_exclusive_taint(self):
        """Make sure that mutually exclusive blocks are recognized during taint analysis."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'mutually-exclusive-taint.c']),
                               'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.fix_object_names(method)
            all_sources = analysis.find_sources(method)
            all_sinks = analysis.find_sinks(method)
            analysis.find_paths_through(method)
            taints = set()
            for path in method.paths:
                method.sources = copy(all_sources)
                method.sinks = copy(all_sinks)
                taints.update(analysis.find_taints(method, path))
            self.assertEqual(len(taints), 0)

    def test_calculate_complexity(self):
        """Make sure that cyclomatic complexity is calculated correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'euclid-complexity.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.calculate_complexity(method)
        self.assertEqual(analysis.methods[0].complexity, 5)

    def test_two_sinks(self):
        """Make sure two sinks of the same type are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'two-sinks.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        sinks = []
        for method in analysis.methods:
            sinks.append(analysis.find_sinks(method))
        count = 0
        for sink in sinks:
            for calls in sink.values():
                for _ in calls:
                    count += 1
        self.assertEqual(count, 2)

    def test_getenv_sprintf(self):
        """Make sure that the combination of a returned source and a sink with the third parameter
        vulnerable on only one path is detected correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'getenv-sprintf.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.fix_object_names(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[0].taints), 1)

    def test_subcall(self):
        """Make sure that calls inside expressions are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'subcall.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.fix_object_names(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[0].taints), 1)

    def test_subsubcall(self):
        """Make sure that subcalls inside expressions are identified correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'subsubcall.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.fix_object_names(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[1].taints), 1)

    def test_subsubcall_two_parameters(self):
        """Make sure that subcalls inside expressions at different positions are identified
        correctly.
        """
        input_file = InputFile(os.sep.join(['testfiles', 'analysis',
                                            'subsubcall-two-parameters.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.fix_object_names(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[2].taints), 1)

    def test_subsubcall_harmless(self):
        """Make sure that harmless subcalls inside expressions are not identified as taints."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'subsubcall-harmless.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.fix_object_names(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[2].taints), 0)

    def test_complex_php(self):
        """Make sure that complex PHP files are analyzed correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'complex.php']), 'php')
        grammar = PHPGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('php'))
        try:
            for method in analysis.methods:
                analysis.follow_variables(method)
                analysis.fix_object_names(method)
                analysis.find_sources(method)
                analysis.find_sinks(method)
                analysis.find_sanitizers(method)
                analysis.find_taints(method)
        except:
            self.fail("Had trouble with at least one of the steps.")

    def test_global_taint(self):
        """Make sure globals are recognized correctly."""
        input_file = InputFile(os.sep.join(['testfiles', 'analysis', 'global-taint.c']), 'c')
        grammar = CGrammar(input_file)
        analysis = Analysis(grammar, Ruleset('c'))
        for method in analysis.methods:
            analysis.follow_variables(method)
            analysis.find_sources(method)
            analysis.find_sinks(method)
            analysis.find_sanitizers(method)
            analysis.find_taints(method)
        self.assertEqual(len(analysis.methods[1].taints), 1)
        # We can't know whether global variables have been changed anywhere, so we always have to
        # interpret them as user controlled
        self.assertEqual(len(analysis.methods[2].taints), 1)


if __name__ == '__main__':
    logging.getLogger('taintalyzing')
    logging.basicConfig(level=logging.ERROR)
    unittest.main()
