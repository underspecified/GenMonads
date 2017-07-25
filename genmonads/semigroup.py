from numbers import Number
import operator


class Semigroup(object):
    """
    A type class representing semigroups."""

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'Semigroup'

    def combine(self, other):
        raise NotImplementedError


class NumberAddSemigroup(Semigroup):
    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'NumberAddSemigroup'

    def combine(self, other):
        return operator.add(self, other)


class NumberMultiplySemigroup(Semigroup):
    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'NumberMultiplySemigroup'

    def combine(self, other):
        return operator.mul(self, other)
