# noinspection PyUnresolvedReferences
import typing

A = typing.TypeVar('A')
B = typing.TypeVar('B')
T = typing.TypeVar('T')


class Functor(object):
    """
    A type class representing covariant functors, i.e. things which can be mapped over."""

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'Functor'

    def fproduct(self, f):
        return self.map(lambda x: (x, f(x)))

    # noinspection PyUnusedLocal
    def imap(self, f, fi):
        """
        Applies a pair of functions to the inner value of a invariant functor.

        Args:
            f (Callable[[A],B]): the function to apply to the functor
            fi (Callable[[B],A]): the function to apply to the invariant functor

        Returns:
            Functor[B]: the resulting functor
        """
        return self.map(f)

    def map(self, f):
        """
        Applies a function to the inner value of a functor.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Functor[B]: the resulting functor
        """
        raise NotImplementedError

    @staticmethod
    def lift(f):
        """
        Lifts a function to operate on functors.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Callable[[Functor[A]],Functor[B]]: the resulting functor
        """
        return lambda fa: fa.map(f)
  