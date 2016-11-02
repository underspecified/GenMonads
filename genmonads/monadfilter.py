import typing

from genmonads.monad import Monad

A = typing.TypeVar('A')
B = typing.TypeVar('B')
T = typing.TypeVar('T')


# noinspection PyAbstractClass
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
        return not self.__eq__(self.empty())

    @staticmethod
    def empty():
        """
        Returns:
            MonadFilter[T]: the empty instance for this monad
        """
        raise NotImplementedError

    def exists(self, f):
        """
        Checks if the predicate is `True` for any of this monad's inner values .

        Args:
            f (Callable[[T],bool]): the predicate

        Returns:
            bool: True if the predicate is `True` for any of this monad's inner values
        """
        return True if self.filter(f) else False

    def filter(self, f):
        """
        Filters this monad by applying the predicate `f` to the monad's inner value.
        Returns this monad if the predicate is `True`, this monad's empty instance otherwise.

        Args:
            f (Callable[[T],bool]): the predicate

        Returns:
            MonadFilter[T]: this instance if the predicate is `True` when applied to its inner value,
            otherwise the monad's empty instance
        """
        return self.flat_map(lambda x: self.pure(x) if f(x) else self.empty())
