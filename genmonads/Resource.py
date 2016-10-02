#!/usr/env/python3
# -*- coding: utf-8 -*-

import gzip
# noinspection PyUnresolvedReferences
import sys
# noinspection PyUnresolvedReferences
from typing import TypeVar

from genmonads.Monad import *

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')


class Resource(Monad):
    def __init__(self, resource, op=None, enter=None, exit=None):
        self._resource = resource
        self._enter = enter
        self._exit = exit
        self._op = op if op else lambda x: x
        self._done = None

    def __add__(self, other):
        pass

    def _eval(self):
        if not self._done:
            self._done = self._op(self._resource)
        return self._done

    def __enter__(self):
        if self._enter:
            return self._enter()
        elif hasattr(self._resource, '__enter__'):
            return self._resource.__enter__()
        else:
            return self._resource

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._exit:
            return self._exit(exc_type, exc_val, exc_tb)
        elif hasattr(self._resource, '__exit__'):
            return self._resource.__exit__(exc_type, exc_val, exc_tb)

    def __str__(self):
        return 'Resource(%s)' % self._resource

    def filter(self, f):
        pass

    def flat_map(self, f):
        return Resource(self._resource, lambda r: f(self._op(r)).run(), self._enter, self._exit)

    def flatten(self):
        return self.flat_map(lambda r: r)

    def map(self, f):
        return Resource(self._resource, lambda r: f(self._op(r)), self._enter, self._exit)

    @staticmethod
    def pure(value):
        return Resource(value)

    def run(self):
        self.__enter__()
        result = self._op(self._resource)
        self.__exit__()
        return result

    def to_list(self):
        return [line for line in self.run()]

    def to_generator(self):
        self.__enter__()
        result = self._op(self._resource)
        while True:
            yield result.next()
        self.__exit__()


def get_file_resource(file):
    return Resource(gzip.open(file) if file.endswith('.gz') else open(file, 'rb'))


def get_file_resources(files):
    return [get_file_resource(file) for file in files] if files else [Resource(sys.stdin), ]
