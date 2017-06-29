from genmonads.mlist import *
from genmonads.monad import *
from genmonads.mtry import *
from genmonads.option import *

__all__ = ['Either', 'Left', 'Right', 'left', 'right']


class Either(Monad):
    """
    A type that represents a disjoint union.

    Instances of type `Either[A,B]` are either an instance of `Left[A]` or `Right[B]`.

    Monadic computing is supported with right-biased `map()` and `flat_map()` functions, and for-comprehensions
    can be formed by evaluating generators over monads with the `mfor()` function.
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
        if type(self) == type(other):
            return self.get_or_none() == other.get_or_none()
        else:
            return False

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the monad's name
        """
        return 'Either'

    def cata(self, fa, fb):
        """
        Transforms an `Either[A,B]` instance by applying `fa` to the inner value of instances of Left[A],
        and `fb` to the inner value of instance of Right[B].

        Args:
            fa (Callable[[A],C): the function to apply to instances of `Left[A]`
            fb (Callable[[B],C): the function to apply to instances of `Right[B]`

        Returns:
            C: the resulting `C` instance
        """
        return fb(self.get()) if self.is_right() else fa(self.get())

    def contains(self, elem):
        """
        Checks if any of this monad's inner values is equivalent to `elem`.

        Args:
            elem (T): the element

        Returns:
            bool: True if any of this monad's inner values is equivalent to `elem`
        """
        return self.exists(lambda x: elem == x)

    def exists(self, p):
        """
        Checks if the predicate is `True` for any of this monad's inner values .

        Args:
            p (Callable[[T],bool]): the predicate

        Returns:
            bool: True if the predicate is `True` for any of this monad's inner values
        """
        return self.filter_or_else(p, Left('No match found.')).is_right()

    def filter_or_else(self, p, zero):
        """
        Filters this monad by applying the predicate `p` to the monad's inner value.
        Returns this monad if the predicate is `True`, `zero` otherwise.

        Args:
            p (Callable[[T],bool]): the predicate
            zero (Either[A,B]): the value to return if `filter()` fails

        Returns:
            Either[A,B]: this instance if the predicate is `True` when applied to its inner value,
            otherwise `zero`
        """
        return self if self.exists(p) else Left(zero)

    def flat_map(self, f):
        """
        Applies a function to the inner value of this monad.

        Args:
            f (Callable[[B],Either[AA,BB]]): the function to apply

        Returns:
            Union[Either[A,B],Either[AA,BB]]: the resulting monad
        """
        return f(self.get()) if self.is_right() else self

    def forall(self, p):
        """
        Checks if the predicate is `True` for all of this monad's inner values or the monad is empty.

        Args:
            p (Callable[[T],bool]): the predicate

        Returns:
            bool: True if the predicate is True for all of this monad's inner values or the monad is empty,
            False otherwise
        """
        return self.is_left() or p(self.get())

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

    def to_list(self):
        """
        Converts the `Either` into a python list.

        Returns:
            List[B]: the resulting python list
        """
        return [self.get(), ] if self.is_right() else []

    def to_mlist(self):
        """
        Converts the `Either` into a `List` monad.

        Returns:
            List[B]: the resulting List monad
        """
        return List(*self.to_list())

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
