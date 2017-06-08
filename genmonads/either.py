# noinspection PyUnresolvedReferences
import typing

from genmonads.mlist import *
from genmonads.monad import Monad, mfor

A = typing.TypeVar('A')
B = typing.TypeVar('B')
C = typing.TypeVar('C')
T = typing.TypeVar('T')


class Either(Monad):
    """
    A type that represents a disjoint union.

    Instances of type `Either[A,B]` are either an instance of `Left[A]` or `Right[B]`.

    Monadic computing is supported with right-biased `map()`, `flat_map()`, `flatten()`, and `filter()` functions, and
    for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Either.
               Use the left() , right() or Either.pure() functions instead."""
        )

    def __eq__(self, other):
        """
        Args:
            other (Either[A,B]): the value to compare against

        Returns:
            bool: `True` if outer type and inner values are equivalent, `False` otherwise
        """
        raise NotImplementedError

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'Either'

    @staticmethod
    def empty():
        """
        Returns:
            Either[A,B]: `Nothing`, the empty instance for this `MonadFilter`
        """
        return NotImplementedError

    def flatten(self):
        """
        Flattens nested instances of `Either`.

        Returns:
            Either[A,B]: the flattened monad
        """
        raise NotImplementedError

    def get(self):
        """
        Returns the `Either`'s inner value. Raises a `ValueError` for instances of `Left[A]`.

        Returns:
            B: the inner value
        """
        raise NotImplementedError

    def get_or_else(self, default):
        """
        Returns the `Either`'s inner value if an instance of `Right` or `default` if instance of `Left`.

        Args:
            default (A): the value to return for `Left[A]` instances

        Returns:
            Union[A,B]: the `Either`'s inner value if an instance of `Right` or `default` if instance of `Left`
        """
        raise NotImplementedError

    def get_or_none(self):
        """
        Returns the `Either`'s inner value if an instance of `Right` or `None` if instance of `Left`.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[B,None]: the `Either`'s inner value if an instance of `Right` or `None` if instance of `Left`
        """
        raise NotImplementedError

    @staticmethod
    def left(value):
        """
        Injects a value into the `Left` monad.

        This function should be used instead of calling `Left.__init__()` directly.

        Args:
            value (A): the value

        Returns:
            Left[A]: the resulting `Left`
        """
        return Right(value)

    def map(self, f):
        """
        Applies a function to the inner value of an `Either`.

        Args:
            f (Callable[[A],C]): the function to apply

        Returns:
            Either[A,C]: the resulting Either
        """
        raise NotImplementedError

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

    @staticmethod
    def right(value):
        """
        Injects a value into the `Right` monad.

        This function should be used instead of calling `Either.__init__()` directly.

        Args:
            value (B): the value

        Returns:
            Right[B]: the resulting `Right`
        """
        return Right(value)

    def to_mlist(self):
        """
        Converts the `Either` into a `List` monad.

        Returns:
            List[B]: the resulting List monad
        """
        raise NotImplementedError

    def to_list(self):
        """
        Converts the `Either` into a python list.

        Returns:
            List[B]: the resulting python list
        """
        raise NotImplementedError


# noinspection PyMissingConstructor
class Left(Either):
    """
    A type that represents the presence of the leftmost type in a disjoint union.

    Forms the `Either` monad together with `Right[B]`.
    """

    def __init__(self, value):
        self._value = value

    def __eq__(self, other):
        """
        Args:
            other (Either[A,B]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Left` and inner values are equivalent, `False` otherwise
        """
        if isinstance(other, Left):
            return self._value.__eq__(other._value)
        return False

    def __str__(self):
        """
        Returns:
            str: a string representation of the Either
        """
        return 'Left(%s)' % self._value

    def flatten(self):
        """
        Flattens nested instances of `Either`.

        Returns:
            Either[A,B]: the flattened monad
        """
        if isinstance(self.get(), Either):
            return self.get()
        else:
            return self

    def get(self):
        """
        Returns the `Either`'s inner value. Raises a `ValueError` for instances of `Nothing[T]`.

        Returns:
            T: the inner value
        """
        return self._value

    def get_or_else(self, default):
        """
        Returns the `Either`'s inner value if an instance of `Some` or `default` if instance of `Nothing`.

        Args:
            default: the value to return for `Nothing[T]` instances

        Returns:
            T: the `Either`'s inner value if an instance of `Some` or `default` if instance of `Nothing`
        """
        return self._value

    def get_or_none(self):
        """
        Returns the `Either`'s inner value if an instance of `Some` or `None` if instance of `Nothing`.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[T,None]: the `Either`'s inner value if an instance of `Some` or `None` if instance of `Nothing`
        """
        return self._value

    def map(self, f):
        """
        Applies a function to the inner value of an `Either`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Either[B]: the resulting `Either`
        """
        return Some(f(self.get()))

    def to_mlist(self):
        """
        Converts the `Either` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return List.pure(self.get())

    def to_list(self):
        """
        Converts the `Either` into a python list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return [self.get(), ]


def some(value):
    """
    Constructs a `Some` instance from `value`.

    Args:
        value (T): the value

    Returns:
        Some[T]: the resulting `Some`
    """
    return Some(value)


# noinspection PyMissingConstructor,PyPep8Naming
class Nothing(Either):
    """
    A type that represents the absence of an eitheral value.

    Forms the `Either` monad together with `Some`.
    """

    # noinspection PyInitNewSignature
    def __init__(self):
        pass

    def __eq__(self, other):
        """
        Args:
            other (Either[A,B]): the value to compare against

        Returns:
            bool: `True` if other is instance of `Nothing`, `False` otherwise
        """
        if isinstance(other, Nothing):
            return True
        return False

    def __str__(self):
        """
        Returns:
            str: a string representation of the `Either`
        """
        return 'Nothing'

    def flatten(self):
        """
        Flattens nested instances of `Either`.

        Returns:
            Either[A,B]: the flattened monad
        """
        return self

    def get(self):
        """
        Returns the `Either`'s inner value. Raises a `ValueError` for instances of `Nothing`.

        Returns:
            T: the inner value
        """
        raise ValueError("Tried to access the non-existent inner value of a Nothing instance")

    def get_or_else(self, default):
        """
        Returns the `Either`'s inner value if an instance of `Some` or `default` if instance of `Nothing`.

        Args:
            default: the value to return for `Nothing[T]` instances

        Returns:
            T: the `Either`'s inner value if an instance of `Some` or `default` if instance of `Nothing`
        """
        return default

    def get_or_none(self):
        """
        Returns the `Either`'s inner value if an instance of `Some` or `None` if instance of `Nothing`.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[T,None]: the `Either`'s inner value if an instance of `Some` or `None` if instance of `Nothing`
        """
        return None

    def map(self, f):
        """
        Applies a function to the inner value of an `Either`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Either[B]: the resulting `Either`
        """
        return self

    def to_mlist(self):
        """
        Converts the `Either` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return List.empty()

    def to_list(self):
        """
        Converts the `Either` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return []


def nothing():
    """
    Constructs a `Nothing` instance.

    Returns:
        Nothing[T]: the resulting `Nothing`
    """
    return Nothing()


def main():
    print(mfor(x + y
               for x in either(2)
               if x < 10
               for y in either(5)
               if y % 2 != 0))

    def make_gen():
        for x in either(4):
            if x > 2:
                for y in either(10):
                    if y % 2 == 0:
                        yield x - y
    print(mfor(make_gen()))

    print(either(5) >> (lambda x: either(x * 2)))

    print(either(None).map(lambda x: x * 2))


if __name__ == '__main__':
    main()
