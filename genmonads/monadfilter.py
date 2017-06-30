# noinspection PyUnresolvedReferences
import sys

from genmonads.monad import Monad
from genmonads.tailrec import trampoline

__all__ = ['MonadFilter', ]


class MonadFilter(Monad):
    """
    A base class for monads that can implement a `filter()` function.

    The monad must define an empty instance of the monad that is returned when `filter()` fails and represents a
    `False` value for the monad.
    """

    def __bool__(self):
        """
        Returns:
            bool: `False` if equal to this monad's empty instance, `True` otherwise
        """
        return not self.is_empty()

    def contains(self, x):
        """
        Checks if any of this monad's inner values is equivalent to `x`.

        Args:
            x T: the value

        Returns:
            bool: True if any of this monad's inner values is equivalent to `x`
        """
        return self.exists(lambda xx: x == xx)

    @staticmethod
    def empty():
        """
        Returns:
            MonadFilter[T]: the empty instance for this monad
        """
        raise NotImplementedError

    def exists(self, p):
        """
        Checks if the predicate is `True` for any of this monad's inner values .

        Args:
            p (Callable[[T],bool]): the predicate

        Returns:
            bool: True if the predicate is `True` for any of this monad's inner values
        """
        return self.filter(p).non_empty()

    def filter(self, p):
        """
        Filters this monad by applying the predicate `p` to the monad's inner value.
        Returns this monad if the predicate is `True`, this monad's empty instance otherwise.

        Args:
            p (Callable[[T],bool]): the predicate

        Returns:
            MonadFilter[T]: this instance if the predicate is `True` when applied to its inner value,
            otherwise the monad's empty instance
        """
        return self.flat_map(lambda x: self.pure(x) if p(x) else self.empty())

    def filter_not(self, p):
        """
        Filters this monad by applying the predicate `p` to the monad's inner value.
        Returns this monad if the predicate is `True`, this monad's empty instance otherwise.

        Args:
            p (Callable[[T],bool]): the predicate

        Returns:
            MonadFilter[T]: this instance if the predicate is `True` when applied to its inner value,
            otherwise the monad's empty instance
        """
        return self.flat_map(lambda x: self.pure(x) if not p(x) else self.empty())

    def flat_map(self, f):
        """
        Applies a function to the inner value of a `MonadFilter`.

        Args:
            f (Callable[[B],MonadFilter[C]): the function to apply

        Returns:
            MonadFilter[C]: the resulting monad
        """
        raise NotImplementedError

    def forall(self, p):
        """
        Checks if the predicate is `True` for all of this monad's inner values or the monad is empty.

        Args:
            p (Callable[[T],bool]): the predicate

        Returns:
            bool: True if the predicate is True for all of this monad's inner values or the monad is empty,
            False otherwise
        """
        return self.is_empty() or p(self.get())

    def get(self):
        """
        Returns the `Monad`'s inner value.
        Returns:
            T: the inner value
        """
        raise NotImplementedError

    def is_empty(self):
        """
        Checks if the monad is equal to the empty value for its type class.

        Returns:
            bool: True if the monad is empty, False otherwise
        """
        return self == self.empty()

    def non_empty(self):
        """
        Checks if the monad is unequal to the empty value for its type class.

        Returns:
            bool: True if the monad is non-empty, False otherwise
        """
        return not self.is_empty()

    @staticmethod
    def pure(value):
        """
        Injects a value into the monad.

        Args:
            value (T): the value

        Returns:
            Monad[T]: the monadic value
        """
        raise NotImplementedError

    # noinspection PyPep8Naming
    @staticmethod
    def tailrecM(f, a):
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (Callable[[A],F[Either[A,B]]]): the function to apply
            a: the recursive function's input

        Returns:
            F[B]: an `F` instance containing the result of applying the tail-recursive function to its argument
        """
        def go(a1):
            fa = f(a1)
            if fa.non_empty():
                e = fa.get()
                x = e.get()
                if e.is_left():
                    return lambda: go(x)
                else:
                    return fa.pure(x)
            else:
                return fa
        return trampoline(go, a)
