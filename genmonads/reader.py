from genmonads.monad import Monad
from genmonads.mytypes import *

__all__ = ['Reader', 'reader']


class Reader(Monad[A],
             Generic[A, B]):
    """
    A base class for implementing Readers for other types to depend on.
    """

    def __init__(self, run: F1[A, B]):
        self.run: F1[A, B] = run

    def __eq__(self, other: 'Reader[A, B]') -> bool:
        """
        Args:
            other (Reader[A, B]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Some` and inner values are
                  equivalent, `False` otherwise
        """
        return (type(self) != type(other) and
                self.run and other.run)

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the monad's name
        """
        return 'Reader'

    def flat_map(self, f: F1[B, 'Reader[B, C]']) -> 'Reader[B, C]':
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (F1[[B, Reader[B, C]): the function to apply

        Returns:
            Reader[B, C]: the resulting monad
        """
        return self.run(f)

    def get(self) -> B:
        """
        Returns the `Gettable`'s inner value.

        Returns:
            B: the inner value
        """
        raise NotImplementedError

    def map(self, f: F1[B, C]) -> 'Reader[B, C]':
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (F1[B, C]): the function to apply

        Returns:
            Reader[B, C]: the resulting monad
        """
        return Reader(lambda b: f(self.run(b)))

    @staticmethod
    def pure(run: F1[A, B]) -> 'Reader[A, B]':
        """
        Injects a value into the `Reader` monad.

        Args:
            run (F1[A, B]): the function to run

        Returns:
            Reader[A, B]: the resulting `Reader`
        """
        return Reader(run)


def reader(run: F1[A, B]) -> 'Reader[A, B]':
    """
    Constructs an `Reader` instance from a value.

    This function converts `None` into an instance of `Nothing`. If this
    behavior is undesired, use `Reader.pure()` instead.

    Args:
        run (F1[A, B]): the value

    Returns:
        Reader[A, B]: the resulting `Reader`
    """
    return Reader.pure(run)


def main():
    #from genmonads.syntax import mfor

    print(reader(lambda name: "Hello %s!" % name)
          .run("Eric"))

    print(reader(lambda x: x*x)
          .map(lambda y: y - 10)
          .map(lambda z: "RESULT: %d %d" % (z, z))
          .run(5))


if __name__ == '__main__':
    main()
