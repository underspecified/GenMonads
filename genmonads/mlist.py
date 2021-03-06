import typing

from genmonads.monad import mfor
from genmonads.monadfilter import MonadFilter
from genmonads.mtry import *

A = typing.TypeVar('A')
B = typing.TypeVar('B')
T = typing.TypeVar('T')


class List(MonadFilter):
    """
    A type that represents list of values of the same type.

    Instances are either of type `List[T]` or `Nil[T]`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions, and
    for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *values):
        self._values = list(values)

    def __eq__(self, other):
        """
        Args:
            other (List[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `List` and inner values are equivalent, `False` otherwise
        """
        if isinstance(other, List) and not isinstance(other, Nil):
            return self._values.__eq__(other._values)
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
        return 'List(%s)' % ', '.join(str(v) for v in self._values)

    @staticmethod
    def empty():
        """
        Returns:
            List[T]: `Nil`, the empty instance for this `MonadFilter`
        """
        return Nil()

    def flatten(self):
        """
        Flattens nested instances of `List`.

        If the inner values can be converted to an instance of `List` by having an implementation of
        `to_mlist()`, the inner values will be converted to `List` before flattening. This allows for
        flattening of `List[Option[T]]` into `List[T]`, as is done in Scala.

        Returns:
            List[T]: the flattened monad
        """
        if self and hasattr(self._values[0], 'to_mlist'):
            # noinspection PyProtectedMember
            return List.pure(*[v for vs in self._values for v in vs.to_mlist()._values])
        else:
            return self

    def head(self):
        """
        Returns the first item in the list.

        Returns:
            T: the first item

        Throws:
            IndexError: if the list is empty
        """
        return self._values[0]

    def head_option(self):
        """
        Safely returns the first item in the list by wrapping the attempt in `Option`.

        Returns:
            Option[T]: the first item wrapped in `Some`, or `Nothing` if the list is empty
        """
        return mtry(self.head).to_option()

    def last(self):
        """
        Returns the last item in the list.

        Returns:
            T: the last item

        Throws:
            IndexError: if the list is empty
        """
        return self._values[-1]

    def last_option(self):
        """
        Safely returns the last item in the list by wrapping the attempt in `Option`.

        Returns:
            Option[T]: the first item wrapped in `Some`, or `Nothing` if the list is empty
        """
        return mtry(self.last).to_option()

    def map(self, f):
        """
        Applies a function to the inner value of an `List`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            List[B]: the resulting List
        """
        return List.pure(*(f(v) for v in self._values))

    def mtail(self):
        """
        Returns the tail of the list as a monadic List.

        Returns:
            List[T]: the rest of the nel
        """
        return List.pure(*self._values[1:])

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `List` monad.

        Args:
            *values (T): the values

        Returns:
            List[T]: the resulting `List`
        """
        if values:
            return List(*values)
        else:
            return Nil()

    def tail(self):
        """
        Returns the tail of the list.

        Returns:
            typing.List[T]: the tail of the list
        """
        return self._values[1:]

    def to_list(self):
        """
        Converts the `Option` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return self._values

    def to_mlist(self):
        """
        Converts the `Option` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return self


def mlist(*values):
    """
    Constructs a `List` instance from a tuple of values.

    Args:
        values (Tuple[T]): the values

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
        self.values = []

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

        If the inner values can be converted to an instance of `List` by having an implementation of
        `to_mlist()`, the inner values will be converted to `List` before flattening. This allows for
        flattening of `List[Option[T]]` into `List[T]`, as is done in Scala.

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

    print(mlist(mlist(1, 2, 3, 4, 5), mlist(5, 4, 3, 2, 1)).flat_map(lambda x: x.last_option()))

if __name__ == '__main__':
    main()
