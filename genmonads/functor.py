from genmonads.mytypes import *


class Functor(Generic[T]):
    """
    A type class representing covariant functors, i.e. things which can be
    mapped over."""

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'Functor'

    def fproduct(self, f: Callable[[A], B]) -> 'Functor[Tuple[A, B]]':
        """
        Applies a function to the inner value of a functor and returns a
        product of the function's input and output.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Functor[(A,B)]: the resulting functor
        """
        return self.map(lambda x: (x, f(x)))

    # noinspection PyUnusedLocal
    def imap(self,
             f: Callable[[A], B],
             fi: Callable[[B], A]
             ) -> 'Functor[B]':
        """
        Applies a pair of functions to the inner value of a invariant functor.

        Args:
            f (Callable[[A],B]): the function to apply to the functor
            fi (Callable[[B],A]): the function to apply to the invariant functor

        Returns:
            Functor[B]: the resulting functor
        """
        return self.map(f)

    @staticmethod
    def lift(f: Callable[[A], B]) -> Callable[['Functor[A]'], 'Functor[B]']:
        """
        Lifts a function to operate on functors.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Callable[[Functor[A]],Functor[B]]: the resulting functor
        """
        return lambda fa: fa.map(f)

    def map(self, f: Callable[[A], B]) -> 'Functor[B]':
        """
        Applies a function to the inner value of a functor.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Functor[B]: the resulting functor
        """
        raise NotImplementedError
