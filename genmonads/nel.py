from genmonads.mlist import *
from genmonads.monad import *
from genmonads.mtry import *

__all__ = ['NonEmptyList', 'nel']


class NonEmptyList(Monad):
    """
    A type that represents a non-empty list of a single type.

    Monadic computing is supported with `map()` and `flat_map()` functions, and for-comprehensions can be formed
    by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, head, *tail):
        if not head:
            raise ValueError('Tried to construct an empty NonEmptyList!')
        self.head = head
        self.tail = list(tail)
        self._value = [self.head, ] + self.tail

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
        if type(self) == type(other):
            return self.get_or_none() == other.get_or_none()
        else:
            return False

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'NonEmptyList'

    def __repr__(self):
        """
        Returns:
            str: a string representation of the List
        """
        return 'NonEmptyList(%s)' % ', '.join(repr(v) for v in self.get())

    def filter(self, p):
        """
        Filters this monad by applying the predicate `f` to the monad's inner value.
        Returns this monad if the predicate is `True`, this monad's empty instance otherwise.

        Args:
            p (Callable[[T],bool]): the predicate

        Returns:
            Union[List[T]|Nel[T]]: a list containing all inner values where the predicate is `True`
        """
        res = self.to_mlist().filter(p)
        return res.to_nel().get_or_else(res)

    def flatten(self):
        """
        Flattens nested instances of `NonEmptyList`.

        If the inner values can be converted to an instance of `NonEmptyList` by having an implementation of
        `to_nel()`, the inner values will be converted to `NonEmptyList` before flattening.

        Returns:
            NonEmptyList[T]: the flattened monad
        """
        if self.is_gettable() and all(map(lambda x: hasattr(x, 'to_nel'), self.get())):
            # noinspection PyProtectedMember
            return NonEmptyList.pure(*[y for ys in self.get() for y in ys.to_nel().get()])
        else:
            return self

    def get(self):
        """
        Returns the `Nel`'s inner value.

        Returns:
            list[T]: the inner value
        """
        return self._value

    def is_gettable(self):
        return True

    def last(self):
        """
        Returns the last item in the nel.

        Returns:
            T: the last item
        """
        return self.get()[-1]

    def map(self, f):
        """
        Applies a function to the inner value of a nel.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            NonEmptyList[B]: the resulting NonEmptyList
        """
        return NonEmptyList(*(f(v) for v in self.get()))

    def mtail(self):
        """
        Returns the tail of the nel as a monadic List.

        Returns:
            List[T]: the rest of the nel
        """
        return List(*self.tail)

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `NonEmptyList` monad.

        Args:
            values (T): the values

        Returns:
            NonEmptyList[T]: the resulting `NonEmptyList`
        """
        return NonEmptyList(*values)

    def to_list(self):
        """
        Converts the `NonEmptyList` into a python list.

        Returns:
            typing.List[T]: the resulting python list
        """
        return self.get()

    def to_mlist(self):
        """
        Converts the `NonEmptyList` into a `List` monad.

        Returns:
            List[T]: the resulting List monad
        """
        return List(*self.get())

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
        values (T): the values

    Returns:
        NonEmptyList[T]: the resulting `NonEmptyList`
    """
    return NonEmptyList.pure(*values)


def main():
    print(nel(2, 3).flat_map(lambda x: nel(x + 5)))

    print(mfor(x + y
               for x in nel(2, 4, 6)
               for y in nel(5, 7, 9)))

    def make_gen():
        for x in nel(4):
            for y in nel(10):
                yield x - y
    print(mfor(make_gen()))

    print(nel(5) >> (lambda x: nel(x * 2)))

    print(mtry(lambda: nel().map(lambda x: x * 2)))

    print(nel(nel(1, 2, 3, 4, 5), nel(5, 4, 3, 2, 1)).flatten())

if __name__ == '__main__':
    main()
