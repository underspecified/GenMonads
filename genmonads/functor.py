from genmonads.mytypes import *


class Functor(Generic[A]):
    """
    A type class representing covariant functors, i.e. things which can be
    mapped over."""

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the name of the type class
        """
        return 'Functor'

    def fproduct(self, f: F1[A, B]) -> 'Functor[Tuple[A, B]]':
        """
        Applies a function to the inner value of a functor and returns a
        product of the function's input and output.

        Args:
            f (F1[A, B]): the function to apply

        Returns:
            Functor[Tuple[A, B]]: the resulting functor
        """
        return self.map(lambda x: (x, f(x)))

    # noinspection PyUnusedLocal
    def imap(self,
             f: F1[A, B],
             fi: F1[B, A]
             ) -> 'Functor[B]':
        """
        Applies a pair of functions to the inner value of a invariant functor.

        Args:
            f (F1[A, B]): the function to apply to the functor
            fi (F1[B, A]): the function to apply to the invariant functor

        Returns:
            Functor[B]: the resulting functor
        """
        return self.map(f)

    @staticmethod
    def lift(f: F1[A, B]) -> F1['Functor[A]', 'Functor[B]']:
        """
        Lifts a function to operate on functors.

        Args:
            f (F1[A, B]): the function to apply

        Returns:
            F1[[Functor[A], Functor[B]]: the resulting functor
        """
        return lambda fa: fa.map(f)

    def map(self, f: F1[A, B]) -> 'Functor[B]':
        """
        Applies a function to the inner value of a functor.

        Args:
            f (F1[A, B]): the function to apply

        Returns:
            Functor[B]: the resulting functor
        """
        raise NotImplementedError
