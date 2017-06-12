# noinspection PyUnresolvedReferences
import typing

from genmonads.mlist import *
from genmonads.monad import *
from genmonads.mtry import *
from genmonads.option import *

A = typing.TypeVar('A')
AA = typing.TypeVar('AA')
B = typing.TypeVar('B')
BB = typing.TypeVar('BB')
C = typing.TypeVar('C')


class Either(Monad):
    """
    A type that represents a disjoint union.

    Instances of type `Either[A,B]` are either an instance of `Left[A]` or `Right[B]`.

    Monadic computing is supported with right-biased `map()`, `flat_map()`, `flatten()`, and `filter()` functions,
    and for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Either.
               Use the left() , right() or Either.pure() functions instead."""
        )

    def __eq__(self, other):
        """
        Args:
            other (Either[AA,BB]): the value to compare against

        Returns:
            bool: `True` if outer type and inner values are equivalent, `False` otherwise
        """
        if self.is_left() and other.is_left():
            return self.get() == other.get()
        elif self.is_right() and other.is_right():
            return self.get() == other.get()
        else:
            return False

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'Either'

    def contains(self, elem):
        return self.exists(lambda b: b == elem)

    def exists(self, p):
        return True if self.is_right() and p(self.get()) else False

    def filter_or_else(self, p, zero):
        return self if self.exists(p) else Left(zero)

    def flatten(self):
        """
        Flattens nested instances of `Either`.

        Returns:
            Union[Either[A,B],Either[AA,BB]]: the flattened monad
        """
        if self.is_right():
            b = self.get()
            return b if b.is_right() or b.is_left() else self
        else:
            return self

    def fold(self, fa, fb):
        return Right(fb(self.get())) if self.is_right() else Left(fa(self.get()))

    def forall(self, p):
        return True if self.is_left() or p(self.get()) else False

    def get(self):
        """
        Returns the `Either`'s inner value.

        Returns:
            Union[A,B]: the inner value
        """
        raise NotImplementedError

    def get_or_else(self, default):
        """
        Returns the `Either`'s inner value if an instance of `Right` or `default` if instance of `Left`.

        Args:
            default (C): the value to return for `Left[A]` instances

        Returns:
            Union[B,C]: the `Either`'s inner value if an instance of `Right` or `default` if instance of `Left`
        """
        return self.get() if self.is_right() else default

    def get_or_none(self):
        """
        Returns the `Either`'s inner value if an instance of `Right` or `None` if instance of `Left`.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[B,None]: the `Either`'s inner value if an instance of `Right` or `None` if instance of `Left`
        """
        return self.get_or_else(None)

    def is_gettable(self):
        return True

    def is_left(self):
        """
        Returns:
            bool: `True` if instance of `Left`, `False` otherwise
        """
        return isinstance(self, Left)

    def is_right(self):
        """
        Returns:
            bool: `True` if instance of `Right`, `False` otherwise
        """
        return isinstance(self, Right)

    def map(self, f):
        """
        Applies a function to the inner value of an `Either`.

        Args:
            f (Callable[[B],C]): the function to apply

        Returns:
            Either[A,C]: the resulting Either
        """
        return Right(f(self.get())) if self.is_right() else self

    @staticmethod
    def pure(value):
        """
        Injects a value into the `Either` monad.

        This function should be used instead of calling `Either.__init__()` directly.

        Args:
            value (B): the value

        Returns:
            Right[B]: the resulting `Right`
        """
        return Right(value)

    def swap(self):
        """
        Converts a `Left` monad to `Right` and vice versa.

        Returns:
            Either[B,A]: the swapped `Either`
        """
        return Left(self.get()) if self.is_right() else Right(self.get())

    def to_mlist(self):
        """
        Converts the `Either` into a `List` monad.

        Returns:
            List[B]: the resulting List monad
        """
        return List(*self.to_list())

    def to_list(self):
        """
        Converts the `Either` into a python list.

        Returns:
            List[B]: the resulting python list
        """
        return [self.get(), ] if self.is_right() else []

    def to_option(self):
        """
        Converts the `Either` into `Some` if an instance of `Right` and `Nothing` if an instance of `Left`.

        Returns:
            Option[B]: the resulting `Option`
        """
        return Some(self.get()) if self.is_right() else Nothing()

    def to_try(self, ex):
        """
        Converts the `Either` into `Success` if an instance of `Right` and `ex` wrapped in `Failure`
        if an instance of `Left`.

        Returns:
            Try[B]: the resulting `Try`
        """
        return Success(self.get()) if self.is_right() else Failure(ex)


# noinspection PyMissingConstructor
class Left(Either):
    """
    A type that represents the presence of the leftmost type in a disjoint union.

    Forms the `Either` monad together with `Right[B]`. Idiomatically, Left[A] is
    used to represent computations that failed.
    """

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        """
        Returns:
            str: a string representation of the Either
        """
        return 'Left(%s)' % repr(self.get())

    def get(self):
        """
        Returns the `Either`'s inner value. Raises a `ValueError` for instances of `Nothing[T]`.

        Returns:
            T: the inner value
        """
        return self._value


def left(value):
    """
    Constructs a `Left` instance from `value`.

    Args:
        value (A): the value

    Returns:
        Left[A]: the resulting `Left`
    """
    return Left(value)


# noinspection PyMissingConstructor,PyPep8Naming
class Right(Either):
    """
    A type that represents the presence of the rightmost type in a disjoint union.

    Forms the `Either` monad together with `Left[A]`. Idiomatically, Right[B] is
    used to represent computations that succeeded.
    """

    # noinspection PyInitNewSignature
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        """
        Returns:
            str: a string representation of the `Either`
        """
        return 'Right(%s)' % repr(self.get())

    def get(self):
        """
        Returns the `Either`'s inner value.

        Returns:
            B: the inner value
        """
        return self._value


def right(value):
    """
    Constructs a `Right` instance from `value`.

    Args:
        value (B): the value

    Returns:
        Right[B]: the resulting `Right`
    """
    return Right(value)


def main():
    print(mfor(x + y
               for x in right(2)
               for y in right(5)))

    def make_gen():
        for x in right(4):
            for y in left('oops'):
                yield x - y
    print(mfor(make_gen()))

    print(right(5) >> (lambda x: right(x * 2)))

    print(left('error').map(lambda x: x * 2))


if __name__ == '__main__':
    main()
