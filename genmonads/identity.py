from genmonads.mlist import *
from genmonads.mtry import *
from genmonads.option import *
from genmonads.monad import *

__all__ = ['Identity', 'identity']


class Identity(Monad):
    """
    A type that represents a value.

    Monadic computing is supported with `map()` and `flat_map()`, and for-comprehensions can be formed by evaluating
    generators over monads with the `mfor()` function.
    """

    def __init__(self, value):
        self._value = value

    def __eq__(self, other):
        """
        Args:
            other (Identity[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Identity` and inner values are equivalent, `False` otherwise
        """
        if type(self) == type(other):
            return self.get_or_none() == other.get_or_none()
        else:
            return False

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the monad's name
        """
        return 'Identity'

    def __repr__(self):
        """
        Returns:
            str: a string representation of the Identity
        """
        return 'Identity(%s)' % repr(self.get())

    def flat_map(self, f):
        """
        Applies a function to the inner value of a monad.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            FlatMap[B]: the resulting monad
        """
        x = self.get()
        return x.map(f) if type(x) == Identity else f(x)

    def get(self):
        """
        Returns the `Gettable`'s inner value.
        Returns:
            T: the inner value
        """
        return self._value

    def map(self, f):
        """
        Applies a function to the inner value of an `Identity`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Identity[B]: the resulting Identity
        """
        return Identity(f(self.get()))

    def is_defined(self):
        return self.is_gettable()

    def is_empty(self):
        return not self.is_gettable()

    def is_gettable(self):
        return True

    def is_identity(self):
        return isinstance(self, Identity)

    @staticmethod
    def pure(value):
        """
        Injects a value into the `Identity` monad.

        Args:
            value (T): the value

        Returns:
            Identity[T]: the resulting `Identity`
        """
        return Identity(value)

    def to_list(self):
        """
        Converts the `Identity` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return [self.get(), ]

    def to_mlist(self):
        """
        Converts the `Identity` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return List(*self.to_list())

    def to_mtry(self):
        """
        Converts the `Identity` into a `Try` monad.

        Returns:
            Self[A]: the resulting Try monad
        """
        return Success(self.get())

    def to_option(self):
        """
        Converts the `Identity` into a `Option` monad.

        Returns:
            Self[A]: the resulting Option monad
        """
        return Some(self.get())


def identity(value):
    """
    Constructs an `Identity` instance from a value.

    Args:
        value (T): the value

    Returns:
        Identity[T]: the resulting `Identity`
    """
    return Identity.pure(value)


def main():
    print(mfor(x + y
               for x in identity(2)
               for y in identity(5)))

    def make_gen():
        for x in identity(4):
            for y in identity(10):
                yield x - y
    print(mfor(make_gen()))

    print(identity(5) >> (lambda x: identity(x * 2)))

    print(mtry(lambda: identity(None).map(lambda x: x * 2)))


if __name__ == '__main__':
    main()
