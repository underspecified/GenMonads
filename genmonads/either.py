from genmonads.eval import Eval
from genmonads.foldable import Foldable
from genmonads.monad import Monad
from genmonads.mtry_base import Try, Failure, Success
from genmonads.mytypes import *
from genmonads.option import Option, Some, Nothing

__all__ = ['Either', 'Left', 'Right', 'left', 'right']


class Either(Foldable,
             Monad,
             Generic[A, B]):
    """
    A type that represents a disjoint union.

    Instances of type `Either[A, B]` are either an instance of `Left[A]` or
    `Right[B]`.

    Monadic computing is supported with right-biased `map()` and `flat_map()`
    functions, and for-comprehensions can be formed by evaluating generators
    over monads with the `mfor()` function.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Either.
               Use the left() , right() or Either.pure() functions instead."""
        )

    def __eq__(self, other: 'Either[AA, BB]') -> bool:
        """
        Args:
            other (Either[AA, BB]): the value to compare against

        Returns:
            bool: `True` if outer type and inner values are equivalent, `False`
                  otherwise
        """
        return (type(self) == type(other) and
                self.get_or_none() == other.get_or_none())

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the monad's name
        """
        return 'Either'

    def cata(self, fa: Callable[[A], C], fb: Callable[[B], C]) -> C:
        """
        Transforms an `Either[A,B]` instance by applying `fa` to the inner
        value of instances of Left[A], and `fb` to the inner value of instance
        of Right[B].

        Args:
            fa (Callable[[A], C]): the function to apply to instances of `Left[A]`
            fb (Callable[[B], C]): the function to apply to instances of `Right[B]`

        Returns:
            C: the resulting C instance
        """
        return fb(self.get()) if self.is_right() else fa(self.get())

    def filter_or_else(self,
                       p: Callable[[A], bool],
                       zero: 'Either[A, B]'
                       ) -> 'Either[A, B]':
        """
        Filters this monad by applying the predicate `p` to the monad's inner
        value. Returns this monad if the predicate is `True`, `zero` otherwise.

        Args:
            p (Callable[[A],bool]): the predicate
            zero (Either[A,B]): the value to return if `filter()` fails

        Returns:
            Either[A,B]: this instance if the predicate is `True` when applied
            to its inner value, otherwise `zero`
        """
        return self if self.exists(p) else Left(zero)

    def flat_map(self,
                 f: Callable[[B], 'Either[AA, BB]']
                 ) -> Union['Either[A, B]', 'Either[AA, BB]']:
        """
        Applies a function to the inner value of this monad.

        Args:
            f (Callable[[B], Either[AA, BB]]): the function to apply

        Returns:
            Union[Either[A, B], Either[AA, BB]]: the resulting monad
        """
        return f(self.get()) if self.is_right() else self

    def fold_left(self, b: B, f: Callable[[B, A], B]) -> B:
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (Callable[[B, A], B]): the function to fold with

        Returns:
            B: the result of folding
        """
        return f(b, self.get()) if self.is_right() else b

    def fold_right(self,
                   lb: 'Eval[B]',
                   f: Callable[[A, 'Eval[B]'], 'Eval[B]']
                   ) -> 'Eval[B]':
        """
        Performs left-associated fold using `f`. Uses lazy evaluation,
        requiring type `Eval[B]` for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (Callable[[A, Eval[B]], Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        return f(self.get(), lb) if self.is_right() else lb

    def get(self) -> Union[A, B]:
        """
        Returns the `Either`'s inner value.

        Returns:
            Union[A, B]: the inner value
        """
        raise NotImplementedError

    def get_or_else(self, default: C) -> 'Union[B, C]':
        """
        Returns the `Either`'s inner value if an instance of `Right` or
        `default` if instance of `Left`.

        Args:
            default (C): the value to return for `Left[A]` instances

        Returns:
            Union[B, C]: the `Either`'s inner value if an instance of `Right` or
            `default` if instance of `Left`
        """
        return self.get() if self.is_right() else default

    def get_or_none(self) -> Optional[B]:
        """
        Returns the `Either`'s inner value if an instance of `Right` or `None`
        if instance of `Left`.

        Provided as interface to code that expects `None` values.

        Returns:
            Optional[B]: the `Either`'s inner value if an instance of `Right`
            or `None` if instance of `Left`
        """
        return self.get_or_else(None)

    def is_left(self) -> bool:
        """
        Returns:
            bool: `True` if instance of `Left`, `False` otherwise
        """
        return isinstance(self, Left)

    def is_right(self) -> bool:
        """
        Returns:
            bool: `True` if instance of `Right`, `False` otherwise
        """
        return isinstance(self, Right)

    @staticmethod
    def pure(value: B) -> 'Right[B]':
        """
        Injects a value into the `Either` monad.

        This function should be used instead of calling `Either.__init__()`
        directly.

        Args:
            value (B): the value

        Returns:
            Right[B]: the resulting `Right`
        """
        return Right(value)

    def swap(self) -> 'Either[B, A]':
        """
        Converts a `Left` monad to `Right` and vice versa.

        Returns:
            Either[B, A]: the swapped `Either`
        """
        return Left(self.get()) if self.is_right() else Right(self.get())

    def to_option(self) -> 'Option[B]':
        """
        Converts the `Either` into `Some` if an instance of `Right` and
        `Nothing` if an instance of `Left`.

        Returns:
            Option[B]: the resulting `Option`
        """
        return Some(self.get()) if self.is_right() else Nothing()

    def to_try(self, ex: Exception) -> 'Try[B]':
        """
        Converts the `Either` into `Success` if an instance of `Right` and `ex`
        wrapped in `Failure` if an instance of `Left`.

        Returns:
            Try[B]: the resulting `Try`
        """
        return Success(self.get()) if self.is_right() else Failure(ex)


# noinspection PyMissingConstructor
class Left(Either[A, B]):
    """
    A type that represents the presence of the leftmost type in a disjoint
    union.

    Forms the `Either` monad together with `Right[B]`. Idiomatically, Left[A]
    is used to represent computations that failed.
    """

    def __init__(self, value: A):
        self._value = value

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the Either
        """
        return 'Left(%s)' % repr(self.get())

    def get(self) -> A:
        """
        Returns the `Either`'s inner value.

        Returns:
            A: the inner value
        """
        return self._value


def left(value: A) -> Left[A, B]:
    """
    Constructs a `Left` instance from `value`.

    Args:
        value (A): the value

    Returns:
        Left[A, B]: the resulting `Left`
    """
    return Left(value)


# noinspection PyMissingConstructor,PyPep8Naming
class Right(Either[A, B]):
    """
    A type that represents the presence of the rightmost type in a disjoint
    union.

    Forms the `Either` monad together with `Left[A]`. Idiomatically, Right[B]
    is used to represent computations that succeeded.
    """

    # noinspection PyInitNewSignature
    def __init__(self, value: B):
        self._value = value

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the `Either`
        """
        return 'Right(%s)' % repr(self.get())

    def get(self) -> B:
        """
        Returns the `Either`'s inner value.

        Returns:
            B: the inner value
        """
        return self._value


def right(value) -> Right[A, B]:
    """
    Constructs a `Right` instance from `value`.

    Args:
        value (B): the value

    Returns:
        Right[A, B]: the resulting `Right`
    """
    return Right(value)


# noinspection PyTypeChecker
def main():
    from genmonads.syntax import mfor

    print(mfor(x + y
               for x in right(2)
               for y in right(5)))

    # noinspection PyTypeChecker
    def make_gen():
        for x in right(4):
            for y in left('oops'):
                yield x - y

    print(mfor(make_gen()))

    print(right(5) >> (lambda x: right(x * 2)))

    print(left('error').map(lambda x: x * 2))


if __name__ == '__main__':
    main()
