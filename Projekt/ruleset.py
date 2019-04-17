# -*- coding: utf-8 -*-
"""A module to hold rules for the analysis of a module."""
from __future__ import annotations
import logging
import os

import yaml

from method import Method
from sink import Sink
from source import Source
from sanitizer import Sanitizer


class Ruleset():
    """Holds all rules for a module."""
    logger = logging.getLogger('taintalyzing')

    def __init__(self, module: str):
        """Constructor for class `Ruleset`.  Load sources and sinks.

        Parameters
        ----------
        module : str
            The module for which to load sources and sinks
        """
        self.module = module
        self.sources = list()
        self.__load_sources()
        self.sinks = list()
        self.__load_sinks()
        self.observers = list()

    def __load_sinks(self):
        """Load sinks for this ruleset."""
        for root, _, files in os.walk(os.sep.join(['modules', self.module, 'sinks'])):
            for file_ in files:
                path = os.path.join(root, file_)
                ext = os.path.splitext(path)[1]
                if ext in ('.yaml', '.yml'):
                    Ruleset.logger.debug('Loading sink from file "%s".', path)
                    with open(path) as stream:
                        self.sinks.append(Sink(yaml.safe_load(stream)))

    def __load_sources(self):
        """Load sources for this ruleset."""
        for root, _, files in os.walk(os.sep.join(['modules', self.module, 'sources'])):
            for file_ in files:
                path = os.path.join(root, file_)
                ext = os.path.splitext(path)[1]
                if ext in ('.yaml', '.yml'):
                    Ruleset.logger.debug('Loading source from file "%s".', path)
                    with open(path) as stream:
                        self.sources.append(Source(yaml.safe_load(stream)))

    def add_source(self, method: Method, source: dict):
        """Add a new source to the list.
        New sources are only relevant if either a method's parameters are used in a source or their
        results are returned.

        Parameters
        ----------
        method : Method
            The method where the source was added
        source : dict
            A dictionary definition of the source as defined in the ruleset
        """
        new_source = Source(source)
        for existing_source in self.sources:
            if existing_source.object_name != new_source.object_name:
                continue
            if new_source.methods == existing_source.methods:
                break
        else:
            # Didn't break above, add new source
            Ruleset.logger.debug('Added a new source.  Notifying observers.')
            self.sources.append(new_source)
            self.notify_observers(method, new_source=True)

    def add_sink(self, method: Method, sink: dict):
        """Add a new sink to the list.
        New sinks are only relevant if a method's parameters are used in a sink.
        The same sanitizers are used from the original sink.

        Parameters
        ----------
        method : Method
            The method where the sink was added
        sink : dict
            A dictionary definition of the sink as defined in the ruleset
        """
        new_sink = Sink(sink)
        for existing_sink in self.sinks:
            if existing_sink.object_name != new_sink.object_name:
                continue
            if new_sink.methods == existing_sink.methods:
                break
        else:
            # Didn't break above, add new sink
            Ruleset.logger.debug('Added a new sink.  Notifying observers.')
            self.sinks.append(new_sink)
            self.notify_observers(method)

    def add_sanitizer(self, method: Method, sink: Sink, sink_method_idx: int, sanitizer: dict,
                      level: int = 0):
        """Add a new sanitizer to a sink.
        New sanitizers are only relevant if a method's parameters are used in a sanitizer.

        Parameters
        ----------
        method : Method
            The method where the sanitizer was added
        sink : Sink
            The sink to add the sanitizer to
        sink_method_idx : int
            The index of the method for which to add the new sanitizer
        sanitizer : dict
            A dictionary definition of the sanitizer as defined in the ruleset
        level : int, optional
            The depth of the nesting before the sanitizer is reached (sanitizers defined in the
            rules get a level of 0, sanitizers that call those get a level of 1, sanitizers that
            call those get a level of 2 and so on)
        """
        new_sanitizer = Sanitizer(sanitizer, level)
        duplicate = False
        for existing_sanitizer in sink.methods[sink_method_idx]['Sanitizers']:
            if existing_sanitizer.object_name != new_sanitizer.object_name:
                continue
            if new_sanitizer.methods == existing_sanitizer.methods:
                duplicate = True
                break
        if not duplicate:
            sink.methods[sink_method_idx]['Sanitizers'].append(new_sanitizer)
            self.notify_observers(method, changed_sanitizer=True)

    def register_observer(self, observer):
        """Register an observer for sources and sinks.

        Parameters
        ----------
        observer
            Object that wants to be notified about changes in sources, sinks or sanitizers
        """
        self.observers.append(observer)

    def notify_observers(self, method: Method, changed_sanitizer: bool = None, new_source: bool =
                         False):
        """Notify observers about changes in sinks or sanitizers.

        Parameters
        ----------
        method : Method
            The method that was updated
        changed_sanitizer : bool, optional
            A sanitizer was changed
        new_source : bool, optional
            A new source was added
        """
        for observer in self.observers:
            observer.update(method, changed_sanitizer=changed_sanitizer, new_source=new_source)
