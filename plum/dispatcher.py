# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import logging

from .function import Function
from .tuple import Tuple
from .type import as_type
from .util import get_default

__all__ = ['Dispatcher', 'dispatch']
log = logging.getLogger(__name__)


class Dispatcher(object):
    """A namespace for functions.

    Args:
        in_class (type, optional): Class to which the namespace is associated.
    """

    def __init__(self, in_class=None):
        self._functions = {}
        self._class = in_class

    def __call__(self, *types, **kw_args):
        """Create a decorator for a particular signature.

        Args:
            *types (type): Types of the signatures.
            precedence (int, optional): Precedence of the signature. Defaults to
                `0`.
            return_type (type, optional): Expected return type. Defaults to
                `object.`

        Returns:
            function: Decorator.
        """
        precedence = get_default(kw_args, 'precedence', 0)
        return_type = get_default(kw_args, 'return_type', object)
        return self._create_decorator([Tuple(*types)],
                                      precedence=precedence,
                                      return_type=as_type(return_type))

    def multi(self, *signatures, **kw_args):
        """Create a decorator for multiple given signatures.

        Args:
            *tuple[type] (type): Signatures.
            precedence (int, optional): Precedence of the signatures. Defaults
                to `0`.
            return_type (type, optional): Expected return type. Defaults to
                `object.`

        Returns:
            function: Decorator.
        """
        precedence = get_default(kw_args, 'precedence', 0)
        return_type = get_default(kw_args, 'return_type', object)
        return self._create_decorator([Tuple(*types) for types in signatures],
                                      precedence=precedence,
                                      return_type=as_type(return_type))

    def _create_decorator(self, signatures, precedence, return_type):
        def decorator(f):
            name = f.__name__

            # Create a new function only if the function does not already exist.
            if name not in self._functions:
                self._functions[name] = Function(f, in_class=self._class)

            # Register the new method.
            for signature in signatures:
                self._functions[name].register(signature,
                                               f,
                                               precedence,
                                               return_type)

            # Return the function.
            return self._functions[name]

        return decorator

    def clear_cache(self):
        """Clear cache."""
        for f in self._functions.values():
            f.clear_cache()

    @staticmethod
    def clear_all_cache():
        """Clear all cache."""
        for f in Function._instances:
            f.clear_cache()


dispatch = Dispatcher()  #: A default dispatcher for convenience purposes.
