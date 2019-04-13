# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import logging

from .type import as_type, VarArgs
from .util import Comparable, multihash

__all__ = ['Tuple']
log = logging.getLogger(__name__)


class Tuple(Comparable):
    """Tuple.

    Args:
        *types (type or ptype): Types of the arguments.
    """

    def __init__(self, *types):
        # Ensure that all types are types.
        self.types = tuple(as_type(t) for t in types)

        # Ensure that only the last type possibly represents varargs.
        if any([isinstance(t, VarArgs) for t in self.types[:-1]]):
            raise TypeError('Only the last type can represent varargs.')

    def __repr__(self):
        return '({})'.format(', '.join(map(repr, self.types)))

    def __hash__(self):
        return multihash(Tuple, *self.types)

    def __len__(self):
        return len(self.base)

    def expand_varargs_to(self, other):
        """Expand varargs to a given :class:`.tuple.Tuple`.

        Args:
            other (:class:`.tuple.Tuple`): Other tuple to expand to.

        Returns:
            tuple[ptype]: Tuple of Plum types that matches `other`.
        """
        if self.has_varargs():
            expansion_size = max(len(other) - len(self), 0)
            types = self.base + self.types[-1].expand(expansion_size)
            log.debug('Expanded {} as {} for {}.'.format(self, types, other))
            return types
        else:
            return self.base

    def __le__(self, other):
        # Check varargs.
        if self.has_varargs() and not other.has_varargs():
            return False
        elif (self.has_varargs() and
              other.has_varargs() and
              self.varargs_type > other.varargs_type):
            return False

        # Check compatibility.
        if not self.is_compatible(other):
            return False

        # Finally, compare.
        return all([x <= y for x, y in zip(self.expand_varargs_to(other),
                                           other.expand_varargs_to(self))])

    @property
    def base(self):
        """Base of the tuple."""
        return self.types[:-1] if self.has_varargs() else self.types

    def has_varargs(self):
        """Check whether this tuple has varargs.

        Returns:
            bool: `True` if and only if this tuple has varargs.
        """
        return len(self.types) > 0 and isinstance(self.types[-1], VarArgs)

    @property
    def varargs_type(self):
        """Type of the varargs."""
        if not self.has_varargs():
            raise RuntimeError('Type of varargs requested, but tuple does not '
                               'have varargs.')
        return self.types[-1].type

    def is_compatible(self, other):
        """Check whether this tuple is compatible with another one.

        Args:
            other (:class:`.tuple.Tuple`): Other tuple to check compatibility
                with.

        Returns:
            bool: Compatibility.
        """
        return (len(self) == len(other)
                or (len(self) > len(other) and other.has_varargs())
                or (len(self) < len(other) and self.has_varargs()))