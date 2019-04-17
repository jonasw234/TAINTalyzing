# -*- coding: utf-8 -*-
"""This module reads files and detects their module."""
from __future__ import annotations
import collections
import functools
import logging
import os

import magic


class InputFile:
    """This class reads a file and detects its module."""
    logger = logging.getLogger('taintalyzing')
    detection_data = list()

    @staticmethod
    def read_detection_data():
        """Read detection data from file."""
        with open('modules/detection.txt') as file_descriptor:
            file_contents = file_descriptor.readlines()
        for line in file_contents:
            module = line.split(':')[0]
            extensions = [extension.strip() for extension in
                          line.split(':')[1].split(';')[0].split(',')]
            magic_number = line.split(';')[1].strip()
            InputFile.logger.debug('Adding module "%s" with extensions "%s" and magic detection '
                                   'string "%s".', module, extensions, magic_number)
            InputFile.detection_data.append((module, extensions, magic_number))

    @functools.lru_cache(maxsize=1)
    def read_file(self) -> str:
        """Read the file and return its contents.

        Returns
        -------
        str
            Contents of the file
        """
        with open(self.path) as file_descriptor:
            try:
                contents = file_descriptor.read()
                return contents
            except UnicodeDecodeError:
                InputFile.logger.warning('"%s" seems to be a binary file and will be ignored.',
                                         self.path)

    def column_to_line(self, column: int) -> int:
        """Convert `column` to a line number.

        Parameters
        ----------
        column : int
            The column to convert

        Returns
        -------
        int
            The corresponding line number
        """
        return self.read_file()[:column].count('\n') + 1

    def line_to_column(self, line: int) -> int:
        """Return the column number where `line` begins.

        Parameters
        ----------
        line : int
            The line number

        Returns
        -------
        int
            The column number where `line` begins
        """
        start = self.read_file().find('\n')
        while start >= 0 and line - 1 > 1:
            start = self.read_file().find('\n', start + len('\n'))
            line -= 1
        return start

    def detect_filetype(self):
        """Detect the module for the input file."""
        detected_filetype_magic = self.detect_magic_number()
        if not detected_filetype_magic:
            # No known magic number found, try to detect based on extension
            InputFile.logger.warning('No known magic number found for "%s", trying file extension '
                                     'instead.', self.path)
            detected_filetype_extension = self.detect_extension()
            possibilities = detected_filetype_extension
        elif len(detected_filetype_magic) == 1:
            # Magic number seems unique, use it
            possibilities = detected_filetype_magic
        else:
            # Multiple possibilities for magic value, check file extension to see if we can narrow
            # it down
            InputFile.logger.warning('Magic number is not unique for "%s", trying to narrow it '
                                     'down with file extension.', self.path)
            detected_filetype_extension = self.detect_extension()
            possibilities = [possibility for possibility in detected_filetype_extension if
                             possibility[2] == detected_filetype_magic[0][2]]
            possibilities = possibilities or detected_filetype_magic  # In case of no file extension
        if len(possibilities) == 1:
            # Unique filetype detection
            self.module = possibilities[0][0]
            InputFile.logger.info('"%s" detected as "%s".', self.path, self.module)
        else:
            # No reliable detection, use either fallback or heuristic
            InputFile.logger.warning('Filetype for "%s" could not be reliably detected.', self.path)
            if self.fallback_module:
                # Use fallback
                if possibilities and self.fallback_module not in [possible_module[0] for
                                                                  possible_module in possibilities]:
                    InputFile.logger.warning('Multiple possible modules detected for "%s", but '
                                             'fallback module "%s" is not among them.', self.path,
                                             self.fallback_module)
                InputFile.logger.debug('Using fallback detection module "%s".',
                                       self.fallback_module)
                self.module = self.fallback_module
            else:
                # Use heuristic
                InputFile.logger.debug('Falling back to heuristic detection.')
                self.module = self.detect_heuristic(possibilities)

    def detect_extension(self, path: str = None) -> list:
        """Return the extension detection of the file.

        Parameters
        ----------
        path : str, optional
            Path to the file whose extension should be detected

        Returns
        -------
        list
            Available modules for this extension
        """
        if not path:
            path = self.path
        possibilities = list()
        for detection_data in InputFile.detection_data:
            if os.path.splitext(path)[1] in detection_data[1]:
                possibilities.append(detection_data)
        return possibilities

    def detect_magic_number(self, path: str = None) -> list:
        """Return the magic number detection of the file.

        Parameters
        ----------
        path : str, optional
            Path to the file whose extension should be detected

        Returns
        -------
        list
            Available modules for this magic number
        """
        if not path:
            path = self.path
        possibilities = list()
        for detection_data in InputFile.detection_data:
            if detection_data[2] in magic.from_file(path):
                possibilities.append(detection_data)
        return possibilities

    def detect_heuristic(self, possibilities: list = None) -> str:
        """"Try to detect filetype based on other files in the same directory.

        Parameters
        ----------
        possibilities : list, optional
            List of possible detections as generated by other methods

        Returns
        -------
        str
            The best guess for a matching module.  Empty if no other recognizable file
            in the same directory.
        """
        current_directory = os.path.dirname(self.path)
        detections = list()
        # We can't use os.path.walk() here because it traverses into subdirectories which we don't
        # want
        files = [os.path.join(current_directory, file_) for file_ in os.listdir(current_directory)
                 if os.path.isfile(os.path.join(current_directory, file_))]
        for file_ in files:
            # Add all the available detections and check for majority.  This works because narrowing
            # down doesn't change the maximum detection value
            detections.extend(self.detect_extension(file_))
            detections.extend(self.detect_magic_number(file_))
        possible_modules = [entry[0] for entry in detections if not possibilities or entry in
                            possibilities]
        counter = collections.Counter(possible_modules)
        most_common = counter.most_common()
        if most_common:
            # Most common module found
            module = most_common[0][0]
            InputFile.logger.debug('The most common module for files in "%s" seems to be "%s", so '
                                   'this is what we assign to "%s".', current_directory, module,
                                   self.path)
            return counter.most_common()[0][0]
        # No known module found at all
        InputFile.logger.warning('No known module found for files in "%s", so no module will be '
                                 'assigned to "%s".', current_directory, self.path)
        return ''

    def __init__(self, path: str, fallback_module: str = ''):
        """Initialize variables.

        Parameters
        ----------
        path : str
            Path to the input file
        fallback_module : str, optional
            Fallback module detection if automatic detection fails
        """
        self.module = fallback_module
        self.path = path
        self.fallback_module = fallback_module
        if not InputFile.detection_data:
            InputFile.read_detection_data()
