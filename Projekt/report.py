# -*- coding: utf-8 -*-
"""A module to generate reports for the analysis results."""
from __future__ import annotations
import html
from io import TextIOWrapper
import time
import typing

from method import Method
from input_file import InputFile


class Report():
    """Generate reports in various formats."""

    def __init__(self, analyses: list, complexity: int, indirection: int, output: TextIOWrapper):
        """Constructor for class `Report`.

        Receive all the necessary information and save it for output.

        Parameters
        ----------
        analyses : list
            A list of all the analyses to create a report from
        complexity : int
            Report methods with a higher complexity as potentially unsafe
        indirection : int
            Maximum level of indirection before sanitizers are ignored for final verdict
        output : TextIOWrapper
            The file to write the output to
        """
        self.analyses = analyses
        self.complexity = complexity
        self.indirection = indirection
        self.output = output
        self.markup = {'begin': '',
                       'begin_end': '',
                       'new_file': '',
                       'new_file_end': '',
                       'module': '',
                       'module_end': '',
                       'method': '',
                       'method_end': '',
                       'complexity': '',
                       'complexity_end': '',
                       'taints_list': '\n',
                       'taints_list_end': '',
                       'taints_list_after': '',
                       'new_taint': '',
                       'new_taint_end': '',
                       'taint': '',
                       'taint_end': '',
                       'taint_messages': '',
                       'taint_messages_end': '',
                       'sinks_list': '\n',
                       'sinks_list_end': '',
                       'sinks_list_after': '',
                       'new_sink': '',
                       'new_sink_end': '',
                       'sink': '',
                       'sink_end': '',
                       'sink_messages': '',
                       'sink_messages_end': '',
                       'nothing_found': '',
                       'nothing_found_end': '',
                       'end': '\n',
                       'end_end': ''}

    def __report_begin(self) -> str:
        """Return a message for the beginning of the report.

        Returns
        -------
        str
            A message to print at the beginning of the report
        """
        return f'TAINTalyzing report created on {time.strftime("%c")}'

    def __report_complexity(self, complexity: int) -> str:
        """Return method complexity.

        Parameters
        ----------
        complexity : int
            The complexity of the method

        Returns
        -------
        str
            A string with the message for the complexity
        """
        return f'Method has a cyclomatic complexity of {complexity}.'

    def __report_file(self, filename: str) -> str:
        """Return new filename.

        Parameters
        ----------
        filename : str
            The name of the file

        Returns
        -------
        str
            A string with the message about which file the analysis is about
        """
        return f'Start of analysis for {filename}:'

    def __report_method(self, method: Method, file_: InputFile) -> str:
        """Return information about the method.

        Parameters
        ----------
        method : Method
            The method about which information is requested
        file_ : InputFile
            The file where the method resides

        Returns
        -------
        str
            Information about the method
        """
        return f'Analysis results for method "{method.method_name[0]}" (lines ' \
            f'{file_.column_to_line(method.start)} to {file_.column_to_line(method.end)}).'

    def __report_module(self, module: str) -> str:
        """Return detected module.

        Parameters
        ----------
        module : str
            The module that was detected

        Returns
        -------
        str
            A message to indicate which module was used to analyze the file
        """
        return f'The filetype was detected as {module}.'

    def __report_taints(self) -> str:
        """Return pre-taint-list-message.

        Returns
        -------
        str
            A message about which taints were detected (should be followed by a list of taints)
        """
        return 'The following taints were detected:'

    def __report_taint(self, taint: list, file_: InputFile, formatter: typing.Callable = lambda n:
                       n) -> str:
        """Return a detected taint.

        Parameters
        ----------
        taint : list
            The list of calls to this taint that was detected
        file_ : InputFile
            The file where the method resides
        formatter : typing.Callable, optional
            Format the output with this function

        Returns
        -------
        str
            A message about how the taint works
        """
        msgs = []
        for call in taint:
            line = file_.column_to_line(call['Position'][0])
            ident = call['Call'][0]['ident'][0]
            msgs.append(f"{self.markup['taint']}In line {line} a call with potentially user "
                        "controlled input is made to "
                        f"{formatter(ident)}.{self.markup['taint_messages_end']}")
            msgs.append(f"{self.markup['taint_messages']}The following comment is linked to this "
                        f"sink: {formatter(call['Comment'])}{self.markup['taint_messages_end']}")
            if call['Sanitizer'] and call['Sanitizer'].level <= self.indirection:
                msgs.append(f"{self.markup['taint_messages']}The taint seems to be sanitized "
                            "(indirection level: "
                            f"{call['Sanitizer'].level}).{self.markup['taint_messages_end']}")
                severity = 0.5 + min(call['Sanitizer'].level / self.indirection, 1) / 2
                msgs.append(f"{self.markup['taint_messages']}Severity level: "
                            f"{severity:.0%}.{self.markup['taint_messages_end']}")
            else:
                msgs.append(f"{self.markup['taint_messages']}No sanitizer "
                            f"detected.{self.markup['taint_messages_end']}")
                msgs.append(f"{self.markup['taint_messages']}Severity level: "
                            f"100%.{self.markup['taint_messages_end']}")
        msgs[-1] = f"{msgs[-1]}{self.markup['taint_end']}"
        return '\n'.join(msgs)

    def __report_sinks(self):
        """Return pre-sink-list-message.

        Returns
        -------
        str
            A message about which sinks were detected (should be followed by a list of sinks)
        """
        return 'The following sinks were detected:'

    def __report_sink(self, sink: dict, comment: str, method: Method, file_: InputFile, formatter:
                      typing.Callable = lambda n: n) -> str:
        """Return a detected sink.

        Parameters
        ----------
        sink : dict
            The sink that was detected
        comment : str
            Comment for this sink
        method : Method
            The method where the sink was found
        file_ : InputFile
            The file where the method resides
        formatter : typing.Callable, optional
            Format the output with this function

        Returns
        -------
        str
            A message about how the sink works
        """
        msgs = []
        msgs.append(f"{self.markup['sink']}In line {file_.column_to_line(sink[1] + method.start)} "
                    "a call without any detected user controlled input is made to "
                    f"{formatter(sink[0][0]['ident'][0])}.{self.markup['sink_messages_end']}")
        msgs.append(f"{self.markup['sink_messages']}The following comment is linked to this sink: "
                    f"{formatter(comment)}{self.markup['sink_messages_end']}")
        msgs.append(f"{self.markup['sink_messages']}Severity level: "
                    f"50%.{self.markup['sink_messages_end']}")
        msgs[-1] = f"{msgs[-1]}{self.markup['sink_end']}"
        return '\n'.join(msgs)

    def __report_nothing_found(self) -> str:
        """Return nothing found message.

        Returns
        -------
        str
            Nothing found message
        """
        return 'Congratulations, nothing to report for this file.'

    def __report_end(self) -> str:
        """Return message to append to the report.

        Returns
        -------
        str
            Message to append to the report
        """
        return 'Don\'t forget that these results are not necessarily complete and could be ' \
               'missing vulnerabilities.  Additional security checks are highly recommended!'

    def __report_needed(self, method) -> bool:
        """Check if we need to report the method.

        Parameters
        ----------
        method : Method
            Do we need to report this method?

        Returns
        -------
        bool
            True if the method needs to be reported
        """
        if method.complexity >= self.complexity or method.taints or method.sinks:
            return True
        return False

    def __generate_report(self, formatter: typing.Callable = lambda n: n):
        """Generate a report.

        Parameters
        ----------
        formatter : typing.Callable, optional
            A function to format the strings before output
        """
        print(self.markup['begin'], end='', file=self.output)
        print(formatter(self.__report_begin()), end='', file=self.output)
        print(self.markup['begin_end'], file=self.output)
        for analysis in self.analyses:
            print(self.markup['new_file'], end='', file=self.output)
            print(formatter(self.__report_file(analysis.grammar.file_.path)), end='',
                  file=self.output)
            print(self.markup['new_file_end'], file=self.output)
            print(self.markup['module'], end='', file=self.output)
            print(formatter(self.__report_module(analysis.module)), end='', file=self.output)
            print(self.markup['module_end'], file=self.output)
            methods_reported = False
            for method in analysis.methods:
                if self.__report_needed(method):
                    methods_reported = True
                    print(self.markup['method'], end='', file=self.output)
                    print(formatter(self.__report_method(method, analysis.grammar.file_)),
                          end='', file=self.output)
                    print(self.markup['method_end'], file=self.output)
                    if method.complexity >= self.complexity:
                        print(self.markup['complexity'], end='', file=self.output)
                        print(formatter(self.__report_complexity(method.complexity)),
                              end='', file=self.output)
                        print(self.markup['complexity_end'], file=self.output)
                    taints_positions = []
                    if method.taints:
                        print(self.markup['taints_list'], end='', file=self.output)
                        print(formatter(self.__report_taints()), end='', file=self.output)
                        print(self.markup['taints_list_end'], file=self.output)
                        for taint in method.taints.values():
                            for call in taint:
                                taints_positions.append(call['Position'])
                            print(self.markup['new_taint'], end='', file=self.output)
                            print(self.__report_taint(taint, analysis.grammar.file_,
                                                      formatter=formatter), end='',
                                  file=self.output)
                            print(self.markup['new_taint_end'], file=self.output)
                        print(self.markup['taints_list_after'], file=self.output)
                    first = True
                    sinks = False
                    # Make sure we haven't already output this sink as a taint before
                    last_sink = (-1, '')
                    for sink in method.sinks.values():
                        for idx, sink_method in enumerate(sink):
                            if isinstance(sink_method, str):
                                # Comment
                                continue
                            for taint in method.taints.values():
                                # Taints have an absolute position, sinks have a relative position
                                if (sink_method[1] + method.start,
                                        sink_method[2] + method.start) in taints_positions:
                                    break
                            else:
                                # Didn't break above, so we haven't output this as a taint before
                                if last_sink == (sink_method[1] + method.start, method.method_name):
                                    # Don't print the same sink twice
                                    continue
                                last_sink = (sink_method[1] + method.start, method.method_name)
                                sinks = True
                                if first:
                                    first = False
                                    print(self.markup['sinks_list'], end='', file=self.output)
                                    print(formatter(self.__report_sinks()), end='',
                                          file=self.output)
                                    print(self.markup['sinks_list_end'], file=self.output)
                                print(self.markup['new_sink'], file=self.output)
                                print(self.__report_sink(sink_method, sink[idx + 1], method,
                                                         analysis.grammar.file_,
                                                         formatter=formatter),
                                      end='', file=self.output)
                                print(self.markup['new_sink_end'], file=self.output)
                    if sinks:
                        print(self.markup['sinks_list_after'], file=self.output)
            if not methods_reported:
                print(self.markup['nothing_found'], end='', file=self.output)
                print(formatter(self.__report_nothing_found()), end='', file=self.output)
                print(self.markup['nothing_found_end'], file=self.output)
        print(self.markup['end'], end='', file=self.output)
        print(formatter(self.__report_end()), end='', file=self.output)
        print(self.markup['end_end'], file=self.output)

    def generate_plaintext_report(self):
        """Generate a plaintext report."""
        self.__generate_report()

    def generate_markdown_report(self):
        """Generate a report in markdown format."""
        self.markup['begin'] = '# '
        self.markup['new_file'] = '## '
        self.markup['module_end'] = ''
        self.markup['method'] = '\n### '
        self.markup['taint'] = '- '
        self.markup['taint_messages'] = '  '
        self.markup['sink'] = '- '
        self.markup['sink_messages'] = '  '
        self.markup['nothing_found'] = '/'
        self.markup['nothing_found_end'] = '/'
        self.markup['end'] = '*'
        self.markup['end_end'] = '*'
        self.__generate_report()

    def generate_html_report(self):
        """Generate a report in HTML format."""
        self.markup['begin'] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>TAINTalyzing report</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <img src="logo.png" alt="Logo">
    <h1 id="begin">"""
        self.markup['begin_end'] = '</h1>'
        self.markup['new_file'] = '    <h2 class="new-file">'
        self.markup['new_file_end'] = '</h2>'
        self.markup['module'] = '    <p class="module">'
        self.markup['module_end'] = '</p>'
        self.markup['method'] = '    <h3 class="method">'
        self.markup['method_end'] = '</h3>'
        self.markup['complexity'] = '    <p class="complexity">'
        self.markup['complexity_end'] = '</p>'
        self.markup['taints_list'] = """    <div class="taints">
        <p>"""
        self.markup['taints_list_end'] = """</p>
        <ul>"""
        self.markup['new_taint'] = '            <li class="taint">'
        self.markup['taint_messages_end'] = '<br>'
        self.markup['new_taint_end'] = """
            </li>"""
        self.markup['taints_list_after'] = """        </ul>
    </div>"""
        self.markup['sinks_list'] = """     <div class="sinks">
        <p>"""
        self.markup['sinks_list_end'] = """</p>
        <ul>"""
        self.markup['new_sink'] = '            <li class="sink">'
        self.markup['sink_messages_end'] = '<br>'
        self.markup['new_sink_end'] = """
            </li>"""
        self.markup['sinks_list_after'] = """         </ul>
    </div>"""
        self.markup['nothing_found'] = '<p id="nothing-found">'
        self.markup['nothing_found_end'] = '</p>'
        self.markup['end'] = '    <strong class="end">'
        self.markup['end_end'] = """</strong>
    <script src="customize.js"></script>
</body>
</html>"""
        self.__generate_report(formatter=html.escape)
