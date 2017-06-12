# noinspection PyUnresolvedReferences
import typing

from genmonads.option import *

A = typing.TypeVar('A')
B = typing.TypeVar('B')
T = typing.TypeVar('T')


class Try(MonadFilter):
    """
    A type that represents a failable computation.

    Instances of type `Try[T]` are either instances of `Success[T]` or `Failure[T]`. This monad uses eager evaluation.
    For lazy computations, see the `Task` monad (under construction).

    Instances of `Try[T]` are constructed by passing a computation wrapped in a thunk (i.e. a lambda expression
    with no arguments) to either the `mtry()` or `Try.pure()` or functions. The thunk is evaluated immediately,
    and successful computations return the result wrapped in `Success`, while computations that raise an exception
    return that exception wrapped in `Failure[T]`.

    Monadic computing is supported with `map`, `flat_map()`, `flatten()`, and `filter()` functions, and
    for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Try.
            Use the try_to() or Try.pure() functions instead."""
        )

    def __eq__(self, other):
        """
        Args:
            other (Try[T]): the value to compare against

        Returns:
            bool: `True` if inner values are equivalent, `False` otherwise
        """
        if isinstance(other, Try):
            return self.get().__eq__(other.get())
        return False

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'Try'

    @staticmethod
    def empty():
        """
        Returns:
            Try[T]: `Failure[T]` with a `ValueError`, the empty instance for this `MonadFilter`
        """
        return Failure(ValueError("This Try instance is empty!"))

    def flatten(self):
        """
        Flattens nested instances of `Try`.

        Returns:
            Try[T]: the flattened monad
        """
        raise NotImplementedError

    def get(self):
        """
        Returns the Try's inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        raise NotImplementedError

    def is_gettable(self):
        return True

    def is_failure(self):
        return isinstance(self, Failure)

    def is_success(self):
        return isinstance(self, Success)

    def map(self, f):
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Try[B]: the resulting `Try`
        """
        raise NotImplementedError

    def or_else(self, default):
        """
        Returns the `Try` if an instance of `Success` or `default` if an instance of `Failure` .

        Args:
            default (Try[B]): the monad to return for `Failure[T]` instances

        Returns:
            Try[B]: the resulting `Try`
        """
        raise NotImplementedError

    @staticmethod
    def pure(thunk):
        """
        Evaluates a failable computation in the `Try` monad.

        This function should be used instead of calling `Try.__init__()` directly.

        Args:
            thunk (Callable[[None],T]): the computation

        Returns:
            Try[T]: the resulting `Try`
        """
        try:
            return Success(thunk())
        except Exception as ex:
            return Failure(ex)

    def recover(self, f):
        """
        Recovers from a failed computation by applying `f` to the exception.

        Essentially, a map on the `Failure` instance.

        Args:
            f (Callable[[Exception],B): the function to call on the `Failure[T]`'s exception

        Returns:
            Try[B]: the resulting `Try`
        """
        raise NotImplementedError

    def recover_with(self, f):
        """
        Recovers from a failed computation by applying `f` to the exception.

        Essentially, a flat_map on the `Failure` instance.

        Args:
            f (Callable[[Exception],Try[B]): the function to call on the `Failure[T]`'s exception

        Returns:
            Try[B]: the resulting `Try`
        """
        raise NotImplementedError

    def to_option(self):
        """
        Converts an instance of `Try[T]` to `Option[T]`.

        `Success[T]` is mapped to `Some[T]`, and `Failure[T]` is mapped to `Nothing[T]`.

        Returns:
            Option[T]: the corresponding `Option`
        """
        raise NotImplementedError


def mtry(thunk):
    """
    Evaluates a delayed computation in the `Try` monad.

    Args:
        thunk (Callable[[None],T]): the delayed computation

    Returns:
        Try[T]: the resulting `Try`
    """
    return Try.pure(thunk)


# noinspection PyMissingConstructor
class Success(Try):
    def __init__(self, value):
        self._value = value

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'Try'

    def __str__(self):
        """
        Returns:
            str: a string representation of monad
        """
        return 'Success(%s)' % self._value

    def flatten(self):
        """
        Flattens nested instances of `Try`.

        Returns:
            Try[T]
        """
        if isinstance(self.get(), Try):
            return self.get()
        else:
            return self

    def get(self):
        """
        Returns the `Try`'s inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        return self._value

    # noinspection PyUnusedLocal
    def get_or_else(self, default):
        """
        Returns the `Try`'s inner value if an instance of `Success` or default if instance of `Failure[T]`.

        Args:
            default: the value to return for Failure instances

        Returns:
            T: the `Try`'s inner value if an instance of `Success` or default if instance of `Failure[T]`
        """
        return self._value

    def map(self, f):
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Try[B]: the resulting `Try`
        """
        return Try.pure(lambda: f(self.get()))

    def or_else(self, default):
        """
        Returns the `Try` if an instance of `Success` or `default` if an instance of `Failure` .

        Args:
            default (Try[B]): the monad to return for `Failure[T]` instances

        Returns:
            Try[B]: the resulting `Try`
        """
        return self

    @staticmethod
    def pure(value):
        """
        Injects a value into the `Success` monad.

        Args:
            value (T): the value

        Returns:
            Try[T]: the resulting `Try`
        """
        return Success(value)

    def recover(self, f):
        """
        Recovers from a failed computation by applying `f` to the exception.

        Essentially, a map on the `Failure` instance.

        Args:
            f (Callable[[Exception],B): the function to call on the `Failure[T]`'s exception

        Returns:
            Try[B]: the resulting `Try`
        """
        return self

    def recover_with(self, f):
        """
        Recovers from a failed computation by applying `f` to the exception.

        Essentially, a flat_map on the `Failure` instance.

        Args:
            f (Callable[[Exception],Try[B]): the function to call on the `Failure[T]`'s exception

        Returns:
            Try[B]: the resulting `Try`
        """
        return self

    def to_mlist(self):
        """
        Converts the `Try` into a `List` monad.

        Returns:
            List[A]: the resulting List monad
        """
        return List(self.to_list())

    def to_list(self):
        """
        Converts the `Try` into a list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return [self.get(), ] if self.is_success() else []

    def to_option(self):
        """
        Converts an instance of `Try[T]` to `Option[T]`.

        `Success[T]` is mapped to `Some[T]`, and `Failure[T]` is mapped to `Nothing[T]`.

        Returns:
            Option[T]: the corresponding `Option`
        """
        return Some(self._value)


def success(value):
    """
    Injects a value into the `Success` monad.

    Args:
        value (T): the value

    Returns:
        Try[T]: the resulting monad
    """
    return Success.pure(value)


# noinspection PyMissingConstructor
class Failure(Try):
    def __init__(self, ex):
        self._ex = ex

    def __str__(self):
        """
        Returns:
            str: a string representation of the monad
        """
        return 'Failure(%s)' % self.get()

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'Try'

    def flatten(self):
        """
        Flattens nested instances of `Try`.

        Returns:
            Try[T]: the flattened monad
        """
        return self

    def get(self):
        """
        Returns the `Try`'s inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        return self._ex

    def get_or_else(self, default):
        """
        Returns the `Try`'s inner value if an instance of `Success` or `default` if instance of `Failure`.

        Args:
            default: the value to return for `Failure[T]` instances

        Returns:
            T: the `Try`'s inner value if an instance of `Success` or `default` if instance of `Failure`
        """
        return default

    def map(self, f):
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Try[B]: the resulting `Try`
        """
        return self

    def or_else(self, default):
        """
        Returns the `Try` if an instance of `Success` or `default` if an instance of `Failure` .

        Args:
            default (Try[B]): the monad to return for `Failure[T]` instances

        Returns:
            Try[B]: the resulting `Try`
        """
        return default

    def raise_ex(self):
        """
        Raises this `Failure` instance's exception.

        Raises:
            Exception: the exception
        """
        raise self.get()

    def recover(self, f):
        """
        Recovers from a failed computation by applying `f` to the exception.

        Essentially, a map on the `Failure` instance.

        Args:
            f (Callable[[Exception],B): the function to call on the `Failure[T]`'s exception

        Returns:
            Try[B]: the resulting `Try`
        """
        return Try.pure(lambda: f(self.get()))

    def recover_with(self, f):
        """
        Recovers from a failed computation by applying `f` to the exception.

        Essentially, a flat_map on the `Failure` instance.

        Args:
            f (Callable[[Exception],Try[B]): the function to call on the `Failure[T]`'s exception

        Returns:
            Try[B]: the resulting `Try`
        """
        return self.recover(f).flatten()

    def to_option(self):
        """
        Converts an instance of `Try[T]` to `Option[T]`.

        `Success[T]` is mapped to `Some[T]`, and `Failure[T]` is mapped to `Nothing[T]`.

        Returns:
            Option[T]: the corresponding `Option`
        """
        return Nothing()


def failure(ex):
    """
    Injects an exception into the `Failure` monad.

    Args:
        ex (Exception): the exception

    Returns:
        Failure[T]: the resulting `Failure`
    """
    return Failure.pure(ex)


def main():
    print(mtry(lambda: 2)
          .filter(lambda x: x < 10)
          .flat_map(lambda x: mtry(lambda: 5)
                    .filter(lambda y: y % 2 != 0)
                    .map(lambda y: x + y)))

    print(mfor(x + y
               for x in mtry(lambda: 2)
               if x < 10
               for y in mtry(lambda: 5)
               if y % 2 != 0))

    def make_gen():
        for x in mtry(lambda: 4):
            if x > 2:
                for y in mtry(lambda: 10):
                    if y % 2 == 0:
                        yield x - y
    print(mfor(make_gen()))

    print((mtry(lambda: 5) >> mtry(lambda: 2)))
    print(mtry(lambda: 1 / 0).map(lambda x: x * 2))
    print(mtry(lambda: 1 / 0).or_else(Success(0)))
    print(mtry(lambda: 1 / 0).recover(lambda _: 0))
    print(mtry(lambda: 1 / 0).recover_with(lambda _: Success(0)))


if __name__ == '__main__':
    main()
