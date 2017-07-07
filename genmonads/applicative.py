from genmonads.apply import Apply

__all__ = ['Applicative', ]


# noinspection PyMissingConstructor
class Applicative(Apply):
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

    def ap(self, ff):
        """
        Applies a function in the applicative functor to a value in the applicative functor.

        Args:
            ff (Applicative[Callable[[A],B]]): the function in the applicative functor

        Returns:
            Applicative[B]: the resulting value in the applicative functor
        """
        raise NotImplementedError

    def map(self, f):
        """
        Applies a function to the inner value of a applicative functor.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Applicative[B]: the resulting applicative functor
        """
        return self.ap(Applicative.pure(f))

    @staticmethod
    def pure(value):
        """
        Injects a value into the applicative functor.

        Args:
            value (T): the value

        Returns:
            Functor[T]: the resulting applicative functor
        """
        raise NotImplementedError
