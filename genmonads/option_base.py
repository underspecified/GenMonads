import typing

from genmonads.convertible import Convertible
from genmonads.monadfilter import MonadFilter
from genmonads.mytypes import *

__all__ = ['Nothing', 'Option', 'Some', 'nothing', 'option', 'some']


class Option(MonadFilter[A],
             Convertible[A]):
    """
    A base class for implementing Options for other types to depend on.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Option.
               Use the option() or Option.pure() functions instead."""
        )

    def __eq__(self, other: 'Option[A]') -> bool:
        """
        Args:
            other (Option[A]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Some` and inner values are
                  equivalent, `False` otherwise
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

    def cata(self, f: F1[A, B], default: B) -> B:
        """
        Transforms an `Option[A]` instance by applying `f` to the inner value
        of instances of `Some[A]`, and returning `default` in the case of
        `Nothing`.

        Args:
            f (Callable[[A], B]): the function to apply to instances of `Left[A]`
            default (B): the function to apply to instances of `Right[B]`

        Returns:
            B: the resulting `B` instance
        """
        return f(self.get()) if self.is_defined() else default

    @staticmethod
    def empty() -> 'Option[A]':
        """
        Returns:
            Option[A]: `Nothing`, the empty instance for this `MonadFilter`
        """
        return Nothing()

    def flat_map(self, f: F1[B, 'Option[C]']) -> 'Option[C]':
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[B], Option[C]]): the function to apply

        Returns:
            Option[C]: the resulting monad
        """
        return f(self.get()) if self.is_defined() else self

    def get(self) -> A:
        """
        Returns the `Gettable`'s inner value.

        Returns:
            A: the inner value
        """
        raise NotImplementedError

    def is_defined(self) -> bool:
        return self.is_gettable()

    def is_empty(self) -> bool:
        return not self.is_defined()

    def is_gettable(self) -> bool:
        return isinstance(self, Some)

    @staticmethod
    def pure(value: A) -> 'Option[A]':
        """
        Injects a value into the `Option` monad.

        This function should be used instead of calling `Option.__init__()`
        directly.

        Args:
            value (a): the value

        Returns:
            Option[A]: the resulting `Option`
        """
        return Some(value)

    def to_iterator(self) -> typing.Iterator[A]:
        """
        Converts the `Option` into a python iterator.

        Returns:
            typing.Iterator[A]: the resulting python iterator
        """
        return (x for x in (self.get() if self.non_empty() else []))

    # noinspection PyUnresolvedReferences
    def upgrade(self) -> 'OptionDeluxe[A]':
        from genmonads.option import option as option_deluxe
        return option_deluxe(self.get_or_none())


def option(value: A) -> 'Option[A]':
    """
    Constructs an `Option` instance from a value.

    This function converts `None` into an instance of `Nothing`. If this
    behavior is undesired, use `Option.pure()` instead.

    Args:
        value (A): the value

    Returns:
        Option[A]: the resulting `Option`
    """
    if value is None:
        return nothing()
    else:
        return some(value)


# noinspection PyMissingConstructor
class Some(Option[A]):
    """
    A type that represents the presence of an optional value.

    Forms the `Option` monad together with `Nothing`.
    """

    def __init__(self, value):
        self._value = value

    def __hash__(self):
        return hash(self.__repr__()) ^ hash(self.get())

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the Option
        """
        return 'Some(%s)' % repr(self.get())

    def get(self) -> A:
        """
        Returns the `Option`'s inner value. Raises a `ValueError` for instances
        of `Nothing`.

        Returns:
            A: the inner value
        """
        return self._value


def some(value: A) -> Some[A]:
    """
    Constructs a `Some` instance from `value`.

    Args:
        value (A): the value

    Returns:
        Some[A]: the resulting `Some`
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

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the `Option`
        """
        return 'Nothing'

    def get(self):
        """
        Returns the `Option`'s inner value. Raises a `ValueError` for instances
        of `Nothing`.
        """
        raise ValueError(
            "Tried to access the non-existent inner value of a Nothing instance")

    # noinspection PyMethodMayBeStatic
    def unpack(self):
        return ()


def nothing() -> Nothing:
    """
    Constructs a `Nothing` instance.

    Returns:
        Nothing: the resulting `Nothing`
    """
    return Nothing()


def main():
    from genmonads.syntax import mfor

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
