from genmonads.monad import *

__all__ = ['MonadFilter', 'mfor', 'do']


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
        return True if self.filter(p) else False

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

    def get(self):
        """
        Returns the `Monad`'s inner value.
        Returns:
            T: the inner value
        """
        raise NotImplementedError

    def is_empty(self):
        return self != self.empty()

    def non_empty(self):
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
