#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""  _____  _    ___ _   _ _____     _           _
 |_   _|/ \  |_ _| \ | |_   _|_ _| |_   _ ___(_)_ __   __ _
   | | / _ \  | ||  \| | | |/ _` | | | | |_  / | '_ \ / _` |
   | |/ ___ \ | || |\  | | | (_| | | |_| |/ /| | | | | (_| |
   |_/_/   \_\___|_| \_| |_|\__,_|_|\__, /___|_|_| |_|\__, |
                                    |___/             |___/  1.0
by Jonas A. Wendorf

Usage:
    main.py PATH
            [-i INDIRECTION]
            [-c COMPLEXITY]
            [-f FILETYPE]
            [-l]
            [-o REPORT]
            [-x EXCLUDE ...]
            [-s | -v]

Options:

    -h, --help           Show this screen
    --version            Show version
    -i, --indirection=N  Max levels of indirection before sanitization is ignored [default: 5]
    -c, --complexity=N   Minimum cyclomatic complexity before function gets reported [default: 10]
    -f, --fallback=None  Fall back to this module if automatic detection fails.  Leave blank to use
                         heuristics instead.
    -l, --lazy           Assume single path through each method.  Trades performance for accuracy.
    -o, --output=None    Output report to this file (plaintext, markdown or html, based on
                         extension)
    -x, --exclude=FILES  Exclude files from the analysis (regular expression)
    -s, --silent         Don't print warnings
    -v, --verbose        Verbose output
"""
from __future__ import annotations
from copy import copy
import logging
import importlib
import os
import re
import sys
import traceback

from docopt import docopt
from schema import Schema, And, Or, Use, SchemaError

from input_file import InputFile
from analysis import Analysis
from ruleset import Ruleset
from report import Report


def find_files(path: str, exclude: list = None) -> str:
    """Read all files under `path` and return them.

    Parameters
    ----------
    path : str
        The path where the search should begin.  When a single file is
        referenced, return it instead.
    exclude: list, optional
        Exclude files whose name matches one of the regular expressions in this list.

    Yields
    ------
    str
        Relative path to the file
    """
    logger = logging.getLogger('taintalyzing')
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            logger.debug('Going into "%s" next.', root)
            for filename in files:
                filename = os.path.join(root, filename)
                if not exclude or (exclude and not any(re.search(pattern, filename) for pattern in
                                                       exclude)):
                    yield filename
    else:
        logger.debug('Single filename provided.')
        yield path


def analyze_files(filepath: str, exclude: list, lazy: bool, logger: logging.Logger) -> list:
    """Analyze files for vulnerabilities.

    Parameters
    ----------
    filepath : str
        Path where to find the file(s)
    exclude : list
        List of regular expressions to exclude in `path`
    lazy : bool
        Ignore mutually exclusive paths through methods
    logger : logging.Logger
        The logger to use for runtime output

    Returns
    -------
    list
        List of all the analyses
    """
    analyses = []
    rulesets = dict()
    # Detect files
    for filename in find_files(filepath, exclude=exclude):
        logger.info('Now processing "%s".', filename)
        input_file = InputFile(filename)
        # Prepare file for analysis
        input_file.detect_filetype()
        try:
            grammar_module = importlib.import_module(f'modules.{input_file.module}.grammar')
            grammar = grammar_module.Grammar(input_file)
            logger.info('Starting analysis for "%s".', input_file.path)
            ruleset = rulesets.get(input_file.module)
            if not ruleset:
                # Load new ruleset
                rulesets[input_file.module] = Ruleset(input_file.module)
                ruleset = rulesets[input_file.module]
            analysis = Analysis(grammar, ruleset)
            for method in analysis.methods:
                # Analyze method
                analysis.calculate_complexity(method)
                analysis.follow_variables(method)
                analysis.fix_object_names(method)
                all_sources = analysis.find_sources(method)
                all_sinks = analysis.find_sinks(method)
                all_sanitizers = analysis.find_sanitizers(method)
                if not lazy:
                    analysis.find_paths_through(method)
                else:
                    # Assume single path through method, ignore mutually exclusive paths
                    method.paths = [[(method.start, method.end)]]
                for path in method.paths:
                    # Analyze individual paths through the method
                    method.sources = copy(all_sources)
                    method.sinks = copy(all_sinks)
                    method.sanitizers = copy(all_sanitizers)
                    analysis.find_taints(method, path)
                if len(method.paths) > 1:
                    # We use multiple paths to better detect taints, but we still need all the
                    # sinks, so another round through the whole method is necessary here
                    method.sources = all_sources
                    method.sinks = all_sinks
                    method.sanitizers = all_sanitizers
                    taints = method.taints
                    analysis.find_taints(method, [(method.start, method.end)])
                    method.taints = taints
            analyses.append(analysis)
        except ModuleNotFoundError:
            logger.error('No grammar found for "%s".', input_file.module)
    return analyses


def generate_report(analyses: list, output: str, complexity: int, indirection: int, logger:
                    logging.Logger):
    """Generate a report for all the `analyses`.

    Parameters
    ----------
    analyses : list
        The analyses to put in the report
    output : str
        The output filename, empty means stdout
    complexity : int
        Report methods above this cyclomatic complexity
    indirection : int
        Methods with a sanitizer that is more than this many levels away from the sink will have the
        same severity level as if they had no sanitizer at all
    logger : logging.Logger
        The logger to use for runtime output
    """
    output_filename = output
    if output_filename:
        output = open(output_filename, 'w')
    else:
        output = sys.stdout
    try:
        report = Report(analyses, complexity, indirection, output)
        if output != sys.stdout and os.path.splitext(output_filename)[1].lower() in ['.htm',
                                                                                     '.html']:
            report.generate_html_report()
        elif output != sys.stdout and os.path.splitext(output_filename)[1].lower() in ['.markdown',
                                                                                       '.md']:
            report.generate_markdown_report()
        else:
            report.generate_plaintext_report()
    except IOError as ex:
        logger.error('I/O error (%s): %s.', ex.errno, ex.strerror)
    except:
        logger.error('Unexpected exception: %s.', sys.exc_info()[0])
        traceback.print_exc()
    finally:
        output.close()


def main():
    """Parse command line arguments and run analysis."""
    # Parse command line arguments
    arguments = docopt(__doc__, version='TAINTalyzing 1.0')

    # Validate arguments
    schema = Schema({
        'PATH': And(os.path.exists, error='PATH doesn\'t exist'),
        '--indirection': Or(None, And(Use(int), lambda n: n > 0),
                            error='--indirection should be integer N > 0'),
        '--complexity': Or(None, And(Use(int), lambda n: n > 0),
                           error='--complexity should be integer N > 0'),
        '--fallback': Or(None, And(Use(str), lambda n: n.strip() != ''),
                         error='--fallback should be non-empty string'),
        '--lazy': Or(None, Use(bool), error='--lazy should be Boolean'),
        '--output': Or(None, And(Use(str),
                                 lambda n: os.path.splitext(n)[1] in ['.txt',
                                                                      '.markdown', '.md',
                                                                      '.htm', '.html']),
                       error='--output should be non-empty string'),
        '--exclude': Or(None, And(Use(list), lambda n: all(name.strip() != '' for name in n)),
                        error='--exclude should be non-empty string'),
        '--silent': Or(None, Use(bool),
                       error='--silent should be Boolean'),
        '--verbose': Or(None, Use(bool),
                        error='--verbose should be Boolean')})
    try:
        arguments = schema.validate(arguments)
    except SchemaError as exception:
        print('Error: {}'.format(exception), file=sys.stderr)
        exit(1)

    logger = logging.getLogger('taintalyzing')
    if arguments['--silent']:
        logging.basicConfig(level=logging.ERROR)
    elif arguments['--verbose']:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    analyses = analyze_files(arguments['PATH'], arguments['--exclude'], arguments['--lazy'], logger)

    generate_report(analyses, arguments['--output'], arguments['--complexity'],
                    arguments['--indirection'], logger)


if __name__ == '__main__':
    main()
