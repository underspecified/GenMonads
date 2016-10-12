# noinspection PyUnresolvedReferences
import itertools
from typing import TypeVar


from genmonads import monadfilter
from genmonads.monad import mfor

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')


class List(monadfilter.MonadFilter):
    """
    A type that represents list of values of the same type.

    Instances are either of type `List[T]` or `Nil[T]`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions, and
    for-comprehensions can  be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *values):
        # raise ValueError(
        #     """Tried to call the constructor of abstract base class List.
        #        Use the mlist() or List.pure() functions instead."""
        # )
        self.values = values

    def __eq__(self, other):
        """
        Args:
            other (List[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `List` and inner values are equivalent, `False` otherwise
        """
        if isinstance(other, List) and not isinstance(other, Nil):
            return self.values.__eq__(other.values)
        return False

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'List'

    def __str__(self):
        """
        Returns:
            str: a string representation of the List
        """
        return 'List(%s)' % ', '.join(str(v) for v in self.values)

    @staticmethod
    def empty():
        """
        Returns:
            List[T]: `Nil`, the empty instance for this monad
        """
        return Nil()

    def flatten(self):
        """
        Flattens nested instances of `List`.

        Returns:
            List[T]: the flattened monad
        """
        if self and isinstance(self.values[0], List):
            return List.pure(*[v for vs in self.values for v in vs.values])
        else:
            return self

    def map(self, f):
        """
        Applies a function to the inner value of an `List`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            List[B]: the resulting List
        """
        return List.pure(*(f(v) for v in self.values))

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `List` monad.

        This function should be used instead of calling `List.__init__()` directly.

        Args:
            *values (T): the values

        Returns:
            List[T]: the resulting `List`
        """
        if values:
            return List(*values)
        else:
            return Nil()


def mlist(*values):
    """
    Constructs an `List` instance from a value.

    Args:
        values (T): the values

    Returns:
        List[T]: the resulting `List`
    """
    return List.pure(*values)


# noinspection PyMissingConstructor,PyPep8Naming
class Nil(List):
    """
    A type that represents the absence of an optional value.

    Forms the `List` monad together with `Some`.
    """

    # noinspection PyInitNewSignature
    def __init__(self):
        pass

    def __eq__(self, other):
        """
        Args:
            other (List[T]): the value to compare against

        Returns:
            bool: `True` if other is instance of `Nil`, `False` otherwise
        """
        if isinstance(other, Nil):
            return True
        return False

    def __str__(self):
        """
        Returns:
            str: a string representation of the `List`
        """
        return 'Nil'

    def flatten(self):
        """
        Flattens nested instances of `List`.

        Returns:
            List[T]: the flattened monad
        """
        return self

    def map(self, f):
        """
        Applies a function to the inner value of an `List`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            List[B]: the resulting `List`
        """
        return self


def nil():
    """
    Constructs a `Nil` instance.

    Returns:
        Nil[T]: the resulting `Nil`
    """
    return Nil()


def main():
    print(mlist(2, 3).flat_map(lambda x: List.pure(x + 5)))

    print(mfor(x + y
               for x in mlist(2, 4, 6)
               if x < 10
               for y in mlist(5, 7, 9)
               if y % 2 != 0))

    def make_gen():
        for x in mlist(4):
            if x > 2:
                for y in mlist(10):
                    if y % 2 == 0:
                        yield x - y
    print(mfor(make_gen()))

    print(mlist(5) >> (lambda x: mlist(x * 2)))

    print(nil().map(lambda x: x * 2))


if __name__ == '__main__':
    main()