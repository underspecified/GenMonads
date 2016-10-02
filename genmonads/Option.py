from typing import TypeVar

from genmonads.Monad import *

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')


class Option(Monad):
    """
    A type that represents an optional value. Instances of type Option[T] are either an instance of Some[T] or Nothing.

    Monadic computing is supported with map, flat_map, and flatten functions, and for-comprehensions can be formed by
    evaluating generators over monads with the mfor function.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Option.
               Use the option() or Option.pure functions instead."""
        )

    def __bool__(self):
        """
        Returns:
            bool: True if instance of Some, False if instance of Nothing
        """
        raise NotImplementedError

    def __eq__(self, other):
        """
        Args:
            other (Option[T]): the value to compare against

        Returns:
            bool: True if instance is equivalent to other, False otherwise
        """
        raise NotImplementedError

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'Option'

    def filter(self, f):
        """
        Args:
            f (Callable[[T],bool]): the predicate

        Returns:
            Option[T]: this instance if the predicate is true when applied to its inner value, Nothing otherwise
        """
        raise NotImplementedError

    def flat_map(self, f):
        """
        Applies a function that produces an Option from unwrapped values to an Option's inner value and flattens the
        nested result. Equivalent to self.map(f).flatten()

        Args:
            f (Callable[[A],Option[B]]): the function to apply

        Returns:
            Option[B]
        """
        raise NotImplementedError

    def flatten(self):
        """
        Flattens nested instances of Option. Equivalent to self.flat_map(lambda x: Option.pure(x))

        Returns:
            Option[T]
        """
        raise NotImplementedError

    def get(self):
        """
        Returns the Option's inner value. Raises a ValueError for instances of Nothing.

        Returns:
            T: the inner value
        """
        raise NotImplementedError

    def get_or_else(self, default):
        """
        Returns the Option's inner value if an instance of Some or default if instance of Nothing.

        Args:
            default: the value to return for Nothing instances

        Returns:
            T: the Option's inner value if an instance of Some or default if instance of Nothing
        """
        raise NotImplementedError

    def get_or_none(self):
        """
        Returns the Option's inner value if an instance of Some or None if instance of Nothing. Provided as interface
        to code that expects None values.

        Returns:
            Union[T,None]: the Option's inner value if an instance of Some or None if instance of Nothing
        """
        raise NotImplementedError

    def map(self, f):
        """
        Applies a function to the inner value of an Option.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Option[B]: the resulting Option
        """
        raise NotImplementedError

    @staticmethod
    def pure(value):
        """
        Injects a value into the Option monad. This function should be used instead of calling Option.__init__
        directly.

        Args:
            value (T): the value

        Returns:
            Option[T]: the resulting Option
        """
        return Some(value)


def option(value):
    """
    Constructs an Option instance from value. This function converts None into an instance of Nothing.
    If this behavior is undesired, use Option.pure instead.

    Args:
        value (T): the value

    Returns:
        Option[T]: the resulting Option
    """
    if value is None:
        return Nothing()
    else:
        return Some(value)


# noinspection PyMissingConstructor
class Some(Option):
    """
    A type that represents the presence of an optional value. Forms the Option monad together with Nothing.
    """

    def __init__(self, value):
        self.value = value

    def __bool__(self):
        """
        Returns:
            bool: True if instance of Some, False if instance of Nothing
        """
        return True

    def __eq__(self, other):
        """
        Args:
            other (Option[T]): the value to compare against

        Returns:
            bool: True if other is an instance of Some and inner values are equivalent, False otherwise
        """
        if isinstance(other, Some):
            return self.value.__eq__(other.value)
        return False

    def __str__(self):
        """
        Returns:
            str: a string representation of the Option
        """
        return 'Some(%s)' % self.value

    def filter(self, f):
        """
        Args:
            f (Callable[[T],bool]): the predicate

        Returns:
            Option[T]: this instance if the predicate is true when applied to its inner value, Nothing otherwise
        """
        return self.flat_map(lambda x: Some(x) if f(x) else Nothing())

    def flat_map(self, f):
        """
        Applies a function that produces an Option from unwrapped values to an Option's inner value and flattens the
        nested result. Equivalent to self.map(f).flatten()

        Args:
            f (Callable[[A],Option[B]]): the function to apply

        Returns:
            Option[B]
        """
        return self.map(f).flatten()

    def flatten(self):
        """
        Flattens nested instances of Option. Equivalent to self.flat_map(lambda x: Option.pure(x))

        Returns:
            Option[T]
        """
        if isinstance(self.get(), Option):
            return self.get()
        else:
            return self

    def get(self):
        """
        Returns the Option's inner value. Raises a ValueError for instances of Nothing.

        Returns:
            T: the inner value
        """
        return self.value

    def get_or_else(self, default):
        """
        Returns the Option's inner value if an instance of Some or default if instance of Nothing.

        Args:
            default: the value to return for Nothing instances

        Returns:
            T: the Option's inner value if an instance of Some or default if instance of Nothing
        """
        return self.value

    def get_or_none(self):
        """
        Returns the Option's inner value if an instance of Some or None if instance of Nothing. Provided as interface
        to code that expects None values.

        Returns:
            Union[T,None]: the Option's inner value if an instance of Some or None if instance of Nothing
        """
        return self.value

    def map(self, f):
        """
        Applies a function to the inner value of an Option.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Option[B]: the resulting Option
        """
        return Some(f(self.get()))


# noinspection PyMissingConstructor,PyPep8Naming
class Nothing(Option):
    """
    A type that represents the absence of an optional value. Forms the Option monad together with Some.
    """

    # noinspection PyInitNewSignature
    def __init__(self):
        pass

    def __bool__(self):
        """
        Returns:
            bool: True if instance of Some, False if instance of Nothing
        """
        return False

    def __eq__(self, other):
        """
        Args:
            other (Option[T]): the value to compare against

        Returns:
            bool: True if other is instance of Nothing, False otherwise
        """
        if isinstance(other, Nothing):
            return True
        return False

    def __str__(self):
        """
        Returns:
            str: a string representation of the Option
        """
        return 'Nothing()'

    def filter(self, f):
        """
        Args:
            f (Callable[[T],bool]): the predicate

        Returns:
            Option[T]: this instance if the predicate is true when applied to its inner value, Nothing otherwise
        """
        return self

    def flat_map(self, f):
        """
        Applies a function that produces an Option from unwrapped values to an Option's inner value and flattens the
        nested result. Equivalent to self.map(f).flatten()

        Args:
            f (Callable[[A],Option[B]]): the function to apply

        Returns:
            Option[B]
        """
        return self

    def flatten(self):
        """
        Flattens nested instances of Option. Equivalent to self.flat_map(lambda x: Option.pure(x))

        Returns:
            Option[T]
        """
        return self

    def get(self):
        """
        Returns the Option's inner value. Raises a ValueError for instances of Nothing.

        Returns:
            T: the inner value
        """
        raise ValueError("Tried to access the non-existent inner value of a Nothing instance")

    def get_or_else(self, default):
        """
        Returns the Option's inner value if an instance of Some or default if instance of Nothing.

        Args:
            default: the value to return for Nothing instances

        Returns:
            T: the Option's inner value if an instance of Some or default if instance of Nothing
        """
        return default

    def get_or_none(self):
        """
        Returns the Option's inner value if an instance of Some or None if instance of Nothing. Provided as interface
        to code that expects None values.

        Returns:
            Union[T,None]: the Option's inner value if an instance of Some or None if instance of Nothing
        """
        return None

    def map(self, f):
        """
        Applies a function to the inner value of an Option.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Option[B]: the resulting Option
        """
        return self


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
