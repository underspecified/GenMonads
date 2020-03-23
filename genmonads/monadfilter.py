# noinspection PyUnresolvedReferences
import sys

from genmonads.monad import Monad
from genmonads.mytypes import *
from genmonads.tailrec import trampoline

__all__ = ['MonadFilter', ]


class MonadFilter(Monad[A]):
    """
    A base class for monads that can implement a `filter()` function.

    The monad must define an empty instance of the monad that is returned when
    `filter()` fails and represents a `False` value for the monad.
    """

    def __bool__(self) -> bool:
        """
        Returns:
            bool: `False` if equal to this monad's empty instance,
                  `True` otherwise
        """
        return not self.is_empty()

    def contains(self, x: A) -> bool:
        """
        Checks if any of this monad's inner values is equivalent to `x`.

        Args:
            x (A): the value

        Returns:
            bool: True if any of this monad's inner values is equivalent to `x`
        """
        return self.exists(lambda xx: x == xx)

    @staticmethod
    def empty() -> 'MonadFilter[A]':
        """
        Returns:
            MonadFilter[A]: the empty instance for this monad
        """
        raise NotImplementedError

    def exists(self, p: Predicate[A]) -> bool:
        """
        Checks if the predicate is `True` for any of this monad's inner values.

        Args:
            p (Predicate[A]): the predicate

        Returns:
            bool: True if the predicate is `True` for any of this monad's inner
                  values
        """
        return self.filter(p).non_empty()

    def filter(self, p: Predicate[A]) -> 'MonadFilter[A]':
        """
        Filters this monad by applying the predicate `p` to the monad's inner
        value.
        Returns this monad if the predicate is `True`, this monad's empty
        instance otherwise.

        Args:
            p (Predicate[A]): the predicate

        Returns:
            MonadFilter[T]: this instance if the predicate is `True` when
                            applied to its inner value, otherwise the monad's
                            empty instance
        """
        return self.flat_map(lambda x: self.pure(x) if p(x) else self.empty())

    def filter_not(self, p: Predicate[A]) -> 'MonadFilter[A]':
        """
        Filters this monad by applying the predicate `p` to the monad's inner
        value.
        Returns this monad if the predicate is `True`, this monad's empty
        instance otherwise.

        Args:
            p (Predicate[A]): the predicate

        Returns:
            MonadFilter[A]: this instance if the predicate is `True` when
            applied to its inner value, otherwise the monad's empty instance
        """
        return self.filter(lambda x: not p(x))

    def flat_map(self, f: F1[A, 'MonadFilter[B]']) -> 'MonadFilter[B]':
        """
        Applies a function to the inner value of a `MonadFilter`.

        Args:
            f (F1[A, MonadFilter[B]]): the function to apply

        Returns:
            MonadFilter[B]: the resulting monad
        """
        raise NotImplementedError

    def forall(self, p: Predicate[A]) -> bool:
        """
        Checks if the predicate is `True` for all of this monad's inner values
        or the monad is empty.

        Args:
            p (Predicate[A]): the predicate

        Returns:
            bool: True if the predicate is True for all of this monad's inner
                  values or the monad is empty, False otherwise
        """
        return self.is_empty() or p(self.get())

    def get(self) -> A:
        """
        Returns the `Monad`'s inner value.
        Returns:
            A: the inner value
        """
        raise NotImplementedError

    def is_empty(self) -> bool:
        """
        Checks if the monad is equal to the empty value for its type class.

        Returns:
            bool: True if the monad is empty, False otherwise
        """
        return self == self.empty()

    def non_empty(self) -> bool:
        """
        Checks if the monad is unequal to the empty value for its type class.

        Returns:
            bool: True if the monad is non-empty, False otherwise
        """
        return not self.is_empty()

    @staticmethod
    def pure(value: A) -> 'MonadFilter[A]':
        """
        Injects a value into the monad.

        Args:
            value (A): the value

        Returns:
            MonadFilter[A]: the monadic value
        """
        raise NotImplementedError

    # noinspection PyUnresolvedReferences
    @staticmethod
    def tailrecM(f: F1[A, 'MonadFilter[Either[A, B]]'],
                 a: A
                 ) -> 'MonadFilter[B]':
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (F1[A, MonadFilter[[Either[A, B]]]): the function to apply
            a (A): the recursive function's input

        Returns:
            MonadFilter: an `F` instance containing the result of applying the
                         tail-recursive function to its argument
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
