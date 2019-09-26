import typing

from genmonads.applicative import Applicative
from genmonads.flat_map import FlatMap
from genmonads.gettable import Gettable
from genmonads.mytypes import *

__all__ = ['Monad', ]


class Monad(Applicative,
            FlatMap,
            Gettable,
            Generic[A]):
    """
    A base class for representing monads.

    Monadic computing is supported with `map()` and `flat_map() functions, and
    for-comprehensions can be formed by evaluating generators over monads with
    the `mfor()` function.
    """

    def ap(self, ff: 'Monad[Callable[[A], B]]') -> 'Monad[B]':
        """
        Applies a function in the monad to a value in the monad.

        Args:
            ff (Monad[Callable[[A], B]]): the function in the applicative
                                          functor

        Returns:
            Monad[B]: the resulting value in the applicative functor
        """
        return self.flat_map(lambda a: ff.map(lambda f: f(a)))

    def __iter__(self) -> 'MonadIter[A]':
        """
        Returns:
            MonadIter[A]: a monadic iterator over the content of the monad to support
                          usage in generators
        """
        return MonadIter(self)

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the name of the type class
        """
        return 'Monad'

    def __rshift__(self,
                   f: Union[Callable[[A], 'Monad[B]'], 'Monad[B]']
                   ) -> 'Monad[B]':
        """
        A symbolic alias for `flat_map()`. Uses dynamic type checking to permit
        arguments of the form:

            `self >> lambda x: Monad(x)` and `self >> Monad(x)`.

        Args:
            f (Union[Callable[[A], Monad[B]], Monad[B]]): the function to apply

        Returns:
            Monad[B]
        """
        return f if isinstance(f, Monad) else self.flat_map(f)

    def flat_map(self, f: Callable[[A], 'Monad[B]']) -> 'Monad[B]':
        """
        Applies a function that produces an Monad from unwrapped values to a
        Monad's inner value and flattens the nested result.

        Equivalent to `self.map(f).flatten()`.

        Args:
            f (Callable[[A], Monad[B]]): the function to apply

        Returns:
            Monad[B]: the resulting monad
        """
        raise NotImplementedError

    def get(self) -> A:
        """
        Returns the `Monad`'s inner value.
        
        Returns:
            A: the inner value
        """
        raise NotImplementedError

    def map(self, f: Callable[[A], B]) -> 'Monad[B]':
        """
        Applies a function to the inner value of a monad.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Monad[B]: the resulting monad
        """
        return self.flat_map(lambda a: self.pure(f(a)))

    @staticmethod
    def pure(value: A) -> 'Monad[A]':
        """
        Injects a value into the monad.

        Args:
            value (A): the value

        Returns:
            Monad[A]: the monadic value
        """
        raise NotImplementedError


class MonadIter(typing.Iterator[A]):
    """
    A monadic iterator wrapper class over the content of the monad to support
    usage in generators
    """
    def __init__(self, monad: Monad[A]):
        self.monad = monad

    def __next__(self):
        raise(TypeError('Use mfor(...) function for evaluation'))

    next = __next__
