# noinspection PyUnresolvedReferences
import itertools
from typing import TypeVar


from genmonads import monad, mlist, mtry
from genmonads.monad import mfor

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')


class NonEmptyList(monad.Monad):
    """
    A type that represents a non-empty list of a single type.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions, and
    for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *values):
        if not values:
            raise ValueError('Tried to construct an empty NonEmptyList!')
        self.values = list(values)

    def __bool__(self):
        """
        Returns:
            bool: True; `NonEmptyList` are never empty
        """
        return True

    def __eq__(self, other):
        """
        Args:
            other (NonEmptyList[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `List` and inner values are equivalent, `False` otherwise
        """
        if isinstance(other, NonEmptyList):
            return self.values.__eq__(other.values)
        return False

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'NonEmptyList'

    def __str__(self):
        """
        Returns:
            str: a string representation of the List
        """
        return 'NonEmptyList(%s)' % ', '.join(str(v) for v in self.values)

    def filter(self, f):
        """
        Filters this monad by applying the predicate `f` to the monad's inner value.
        Returns this monad if the predicate is `True`, this monad's empty instance otherwise.

        Args:
            f (Callable[[T],bool]): the predicate

        Returns:
            List[T]: a list containing all inner values where the predicate is `True`
        """
        return self.to_mlist().filter(f)

    def flatten(self):
        """
        Flattens nested instances of `NonEmptyList`.

        If the inner values can be converted to an instance of `NonEmptyList` by having an implementation of
        `to_nel()`, the inner values will be converted to `NonEmptyList` before flattening.

        Returns:
            NonEmptyList[T]: the flattened monad
        """
        if hasattr(self.values[0], 'to_nel'):
            return NonEmptyList.pure(*[v for vs in self.values for v in vs.to_mlist().values])
        else:
            return self

    def head(self):
        """
        Returns the first item in the nel.

        Returns:
            T: the first item
        """
        return self.values[0]

    def last(self):
        """
        Returns the last item in the nel.

        Returns:
            T: the last item
        """
        return self.values[-1]

    def map(self, f):
        """
        Applies a function to the inner value of a nel.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            NonEmptyList[B]: the resulting NonEmptyList
        """
        return NonEmptyList.pure(*(f(v) for v in self.values))

    def mtail(self):
        """
        Returns the tail of the nel as a monadic List.

        Returns:
            List[T]: the rest of the nel
        """
        return mlist.mlist(*self.values[1:])

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `NonEmptyList` monad.

        Args:
            *values (T): the values

        Returns:
            NonEmptyList[T]: the resulting `NonEmptyList`
        """
        return NonEmptyList(*values)

    def tail(self):
        """
        Returns the tail of the nel.

        Returns:
            List[T]: the tail of the nel
        """
        return self.values[1:]

    def to_list(self):
        """
        Converts the `NonEmptyList` into a list.

        Returns:
            List[T]: the resulting python list
        """
        return self.values

    def to_mlist(self):
        """
        Converts the `NonEmptyList` into a `List` monad.

        Returns:
            List[T]: the resulting List monad
        """
        return mlist.mlist(*self.values)

    def to_nel(self):
        """
        Converts the `NonEmptyList` into a `NonEmptyList`.

        Returns:
            NonEmptyList[T]: the resulting nel
        """
        return self


def nel(*values):
    """
    Constructs a `NonEmptyList` instance from a tuple of values.

    Args:
        values (Tuple[T]): the values

    Returns:
        NonEmptyList[T]: the resulting `NonEmptyList`
    """
    return NonEmptyList.pure(*values)


def main():
    print(nel(2, 3).flat_map(lambda x: nel(x + 5)))

    print(mfor(x + y
               for x in nel(2, 4, 6)
               if x < 10
               for y in nel(5, 7, 9)
               if y % 2 != 0))

    def make_gen():
        for x in nel(4):
            if x > 2:
                for y in nel(10):
                    if y % 2 == 0:
                        yield x - y
    print(mfor(make_gen()))

    print(nel(5) >> (lambda x: nel(x * 2)))

    print(mtry.mtry(lambda: nel().map(lambda x: x * 2)))

    print(nel(nel(1, 2, 3, 4, 5), nel(5, 4, 3, 2, 1)).flatten())

if __name__ == '__main__':
    main()
