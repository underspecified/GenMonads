from genmonads.apply import Apply
from genmonads.mytypes import *

__all__ = ['Applicative', ]


# noinspection PyMissingConstructor
class Applicative(Apply,
                  Generic[A]):
    """
    The applicative functor.
    """

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'Applicative'

    def ap(self, ff: 'Applicative[Callable[[A], B]]') -> 'Applicative[B]':
        """
        Applies a function in the applicative functor to a value in the
        applicative functor.

        Args:
            ff (Applicative[Callable[[A],B]]): the function in the applicative
                                               functor

        Returns:
            Applicative[B]: the resulting value in the applicative functor
        """
        raise NotImplementedError

    def map(self, f: Callable[[A], B]) -> 'Applicative[B]':
        """
        Applies a function to the inner value of a applicative functor.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Applicative[B]: the resulting applicative functor
        """
        return self.ap(Applicative.pure(f))

    @staticmethod
    def pure(value: A) -> 'Applicative[A]':
        """
        Injects a value into the applicative functor.

        Args:
            value (A): the value

        Returns:
            Applicative[A]: the resulting applicative functor
        """
        raise NotImplementedError
