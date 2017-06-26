from genmonads.either import *
from genmonads.mlist import *
from genmonads.monadfilter import *
from genmonads.mtry import *

__all__ = ['Nothing', 'Option', 'Some', 'nothing', 'option', 'some']


class Option(MonadFilter):
    """
    A type that represents an optional value.

    Instances of type `Option[T]` are either an instance of `Some[T]` or `Nothing[T]`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions,
    and for-comprehensions can  be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Option.
               Use the option() or Option.pure() functions instead."""
        )

    def __eq__(self, other):
        """
        Args:
            other (Option[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Some` and inner values are equivalent, `False` otherwise
        """
        if type(self) != type(other):
            return False
        elif self.is_defined() and other.is_defined():
            return self.get_or_none() == other.get_or_none()
        elif self.is_empty() and other.is_empty():
            return True
        else:
            return False

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the monad's name
        """
        return 'Option'

    @staticmethod
    def empty():
        """
        Returns:
            Option[T]: `Nothing`, the empty instance for this `MonadFilter`
        """
        return Nothing()

    def flat_map(self, f):
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[B],Option[C]): the function to apply

        Returns:
            Option[C]: the resulting monad
        """
        return f(self.get()) if self.is_defined() else self

    def fold(self, default, f):
        return Some(f(self.get())) if self.is_defined() else default

    def get(self):
        """
        Returns the `Gettable`'s inner value.
        Returns:
            T: the inner value
        """
        raise NotImplementedError

    def is_defined(self):
        return self.is_gettable()

    def is_empty(self):
        return not self.is_defined()

    def is_gettable(self):
        return isinstance(self, Some)

    @staticmethod
    def pure(value):
        """
        Injects a value into the `Option` monad.

        This function should be used instead of calling `Option.__init__()` directly.

        Args:
            value (T): the value

        Returns:
            Option[T]: the resulting `Option`
        """
        return Some(value)

    def to_list(self):
        """
        Converts the `Option` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return [self.get(), ] if self.is_defined() else []

    def to_mlist(self):
        """
        Converts the `Option` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return List(*self.to_list())


def option(value):
    """
    Constructs an `Option` instance from a value.

    This function converts `None` into an instance of `Nothing[T]`. If this behavior is undesired, use
    `Option.pure()` instead.

    Args:
        value (T): the value

    Returns:
        Option[T]: the resulting `Option`
    """
    if value is None:
        return nothing()
    else:
        return some(value)


# noinspection PyMissingConstructor
class Some(Option):
    """
    A type that represents the presence of an optional value.

    Forms the `Option` monad together with `Nothing[T]`.
    """

    def __init__(self, value):
        self._value = value

    def __hash__(self):
        return hash(self.__repr__()) ^ hash(self.get())

    def __repr__(self):
        """
        Returns:
            str: a string representation of the Option
        """
        return 'Some(%s)' % repr(self.get())

    def get(self):
        """
        Returns the `Option`'s inner value. Raises a `ValueError` for instances of `Nothing[T]`.

        Returns:
            T: the inner value
        """
        return self._value


def some(value):
    """
    Constructs a `Some` instance from `value`.

    Args:
        value (T): the value

    Returns:
        Some[T]: the resulting `Some`
    """
    return Some(value)


# noinspection PyMissingConstructor,PyPep8Naming
class Nothing(Option):
    """
    A type that represents the absence of an optional value.

    Forms the `Option` monad together with `Some`.
    """

    # noinspection PyInitNewSignature
    def __init__(self):
        pass

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        """
        Returns:
            str: a string representation of the `Option`
        """
        return 'Nothing'

    def get(self):
        """
        Returns the `Option`'s inner value. Raises a `ValueError` for instances of `Nothing`.

        Returns:
            T: the inner value
        """
        raise ValueError("Tried to access the non-existent inner value of a Nothing instance")

    def unpack(self):
        return ()


def nothing():
    """
    Constructs a `Nothing` instance.

    Returns:
        Nothing[T]: the resulting `Nothing`
    """
    return Nothing()


def main():
    print(mfor(x + y
               for x in option(2)
               if x < 10
               for y in option(5)
               if y % 2 != 0))

    def make_gen():
        for x in option(4):
            if x > 2:
                for y in option(10):
                    if y % 2 == 0:
                        yield x - y
    print(mfor(make_gen()))

    print(option(5) >> (lambda x: option(x * 2)))

    print(option(None).map(lambda x: x * 2))

if __name__ == '__main__':
    main()
