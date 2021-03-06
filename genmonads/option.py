import typing

from genmonads.mlist import *
from genmonads.monad import mfor
from genmonads.monadfilter import MonadFilter

A = typing.TypeVar('A')
B = typing.TypeVar('B')
T = typing.TypeVar('T')


class Option(MonadFilter):
    """
    A type that represents an optional value.

    Instances of type `Option[T]` are either an instance of `Some[T]` or `Nothing[T]`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions, and
    for-comprehensions can  be formed by evaluating generators over monads with the `mfor()` function.
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
        raise NotImplementedError

    def __mname__(self):
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

    def flatten(self):
        """
        Flattens nested instances of `Option`.

        Returns:
            Option[T]: the flattened monad
        """
        raise NotImplementedError

    def get(self):
        """
        Returns the `Option`'s inner value. Raises a `ValueError` for instances of `Nothing[T]`.

        Returns:
            T: the inner value
        """
        raise NotImplementedError

    def get_or_else(self, default):
        """
        Returns the `Option`'s inner value if an instance of `Some` or `default` if instance of `Nothing`.

        Args:
            default (T): the value to return for `Nothing[T]` instances

        Returns:
            T: the `Option`'s inner value if an instance of `Some` or `default` if instance of `Nothing`
        """
        raise NotImplementedError

    def get_or_none(self):
        """
        Returns the `Option`'s inner value if an instance of `Some` or `None` if instance of `Nothing`.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[T,None]: the `Option`'s inner value if an instance of `Some` or `None` if instance of `Nothing`
        """
        raise NotImplementedError

    def map(self, f):
        """
        Applies a function to the inner value of an `Option`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Option[B]: the resulting Option
        """
        raise NotImplementedError

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

    def to_mlist(self):
        """
        Converts the `Option` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        raise NotImplementedError

    def to_list(self):
        """
        Converts the `Option` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        raise NotImplementedError


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

    def __eq__(self, other):
        """
        Args:
            other (Option[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Some` and inner values are equivalent, `False` otherwise
        """
        if isinstance(other, Some):
            return self._value.__eq__(other._value)
        return False

    def __str__(self):
        """
        Returns:
            str: a string representation of the Option
        """
        return 'Some(%s)' % self._value

    def flatten(self):
        """
        Flattens nested instances of `Option`.

        Returns:
            Option[T]: the flattened monad
        """
        if isinstance(self.get(), Option):
            return self.get()
        else:
            return self

    def get(self):
        """
        Returns the `Option`'s inner value. Raises a `ValueError` for instances of `Nothing[T]`.

        Returns:
            T: the inner value
        """
        return self._value

    def get_or_else(self, default):
        """
        Returns the `Option`'s inner value if an instance of `Some` or `default` if instance of `Nothing`.

        Args:
            default: the value to return for `Nothing[T]` instances

        Returns:
            T: the `Option`'s inner value if an instance of `Some` or `default` if instance of `Nothing`
        """
        return self._value

    def get_or_none(self):
        """
        Returns the `Option`'s inner value if an instance of `Some` or `None` if instance of `Nothing`.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[T,None]: the `Option`'s inner value if an instance of `Some` or `None` if instance of `Nothing`
        """
        return self._value

    def map(self, f):
        """
        Applies a function to the inner value of an `Option`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Option[B]: the resulting `Option`
        """
        return Some(f(self.get()))

    def to_mlist(self):
        """
        Converts the `Option` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return List.pure(self.get())

    def to_list(self):
        """
        Converts the `Option` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return [self.get(), ]


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

    def __eq__(self, other):
        """
        Args:
            other (Option[T]): the value to compare against

        Returns:
            bool: `True` if other is instance of `Nothing`, `False` otherwise
        """
        if isinstance(other, Nothing):
            return True
        return False

    def __str__(self):
        """
        Returns:
            str: a string representation of the `Option`
        """
        return 'Nothing'

    def flatten(self):
        """
        Flattens nested instances of `Option`.

        Returns:
            Option[T]: the flattened monad
        """
        return self

    def get(self):
        """
        Returns the `Option`'s inner value. Raises a `ValueError` for instances of `Nothing`.

        Returns:
            T: the inner value
        """
        raise ValueError("Tried to access the non-existent inner value of a Nothing instance")

    def get_or_else(self, default):
        """
        Returns the `Option`'s inner value if an instance of `Some` or `default` if instance of `Nothing`.

        Args:
            default: the value to return for `Nothing[T]` instances

        Returns:
            T: the `Option`'s inner value if an instance of `Some` or `default` if instance of `Nothing`
        """
        return default

    def get_or_none(self):
        """
        Returns the `Option`'s inner value if an instance of `Some` or `None` if instance of `Nothing`.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[T,None]: the `Option`'s inner value if an instance of `Some` or `None` if instance of `Nothing`
        """
        return None

    def map(self, f):
        """
        Applies a function to the inner value of an `Option`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Option[B]: the resulting `Option`
        """
        return self

    def to_mlist(self):
        """
        Converts the `Option` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return List.empty()

    def to_list(self):
        """
        Converts the `Option` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return []


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
