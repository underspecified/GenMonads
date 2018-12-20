import typing

from genmonads.convertible import Convertible
from genmonads.monad import Monad
from genmonads.mytypes import *
from genmonads.option_base import Option, Some, Nothing
from genmonads.util import is_thunk

__all__ = ['Failure', 'Success', 'Try', 'failure', 'mtry', 'success']


class Try(Monad[A],
          Convertible[A]):
    """
    A base class for implementing Trys for other types to depend on.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Try.
            Use the try_to() or Try.pure() functions instead."""
        )

    def __eq__(self, other: 'Try[A]') -> bool:
        """
        Args:
            other (Try[A]): the value to compare against

        Returns:
            bool: `True` if inner values are equivalent, `False` otherwise
        """
        return (type(self) == type(other) and
                self.get_or_none() == other.get_or_none())

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the monad's name
        """
        return 'Try'

    def cata(self, fa: F1[A, B], fb: F1[Exception, B]) -> B:
        """
        Transforms an `Try[A]` instance by applying `fa` to the inner value of
        instances of Success[A], and `fb` to the inner value of instance of
        Failure.

        Args:
            fa (F1[A, B]): the function to apply to instances of `Success[A]`
            fb (F1[Exception, B]): the function to apply to instances of
            `Failure`

        Returns:
            B: the resulting `B` instance
        """
        return fb(self.get()) if self.is_success() else fa(self.get())

    def flat_map(self, f: F1[A, 'Try[B]']) -> 'Try[B]':
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (F1[A, Try[B]]): the function to apply

        Returns:
            Try[B]: the resulting monad
        """
        return f(self.get()) if self.is_success() else self

    def get(self) -> Union[A, Exception]:
        """
        Returns the Try's inner value.

        Returns:
            Union[A, Exception]: the inner value
        """
        raise NotImplementedError

    def is_failure(self) -> bool:
        return isinstance(self, Failure)

    def is_success(self) -> bool:
        return isinstance(self, Success)

    def or_else(self, default: 'Try[A]') -> 'Try[A]':
        """
        Returns the `Try` if an instance of `Success` or `default` if an
        instance of `Failure` .

        Args:
            default (Try[A]): the monad to return for `Failure[A]` instances

        Returns:
            Try[A]: the resulting `Try`
        """
        return self if self.is_success() else default

    @staticmethod
    def pure(value: Union[A, Thunk[A]]) -> 'Try[A]':
        """
        Evaluates a thunk and injects the result into the `Try` monad.

        This function should be used instead of calling `Try.__init__()`
        directly.

        Args:
            value (Union[A, Thunk[A]]): a thunk or value

        Returns:
            Try[A]: the resulting `Try`

        Raises:
            ValueError: if the argument is not a zero arity lambda function
        """
        if is_thunk(value):
            try:
                return Success(value())
            except Exception as ex:
                return Failure(ex)
        else:
            return Success(value)

    def recover(self, f: F1[Exception, B]) -> 'Try[B]':
        """
        Recovers from a failed computation by applying `f` to the exception.

        Essentially, a map on the `Failure` instance.

        Args:
            f (F1[Exception,B]): the function to call on the `Failure[A]`'s
                                 exception

        Returns:
            Try[B]: the resulting `Try`
        """
        return self if self.is_success() else f(self.get())

    def recover_with(self, f: F1[Exception, 'Try[B]']) -> 'Try[B]':
        """
        Recovers from a failed computation by applying `f` to the `Failure`
        instance.

        Essentially, a flat_map on the `Failure` instance.

        Args:
            f (F1[Exception, 'Try[B]']): the function to call on the `Failure`

        Returns:
            Try[B]: the resulting `Try[B]`
        """
        return self if self.is_success() else f(self)

    def to_list(self) -> typing.List[A]:
        """
        Converts an instance of `Try[A]` to a pythonic list.

        `Success[A]` is mapped to a singleton list containing the value,
         and `Failure[A]` is mapped to the empty list.

        Returns:
            typing.List[A]: the corresponding list
        """
        return [self.get(), ] if self.is_success() else []

    def to_option(self) -> 'Option[A]':
        """
        Converts an instance of `Try[A]` to a pythonic list.

        `Success[A]` is mapped to Some[A] containing the value,
         and `Failure[A]` is mapped to Nothing.

        Returns:
            Option[A]: the corresponding Option
        """
        return Some(self.get()) if self.is_success() else Nothing()


def mtry(thunk: Thunk[A]) -> Try[A]:
    """
    Evaluates a failable computation in the `Try` monad.

    This function should be used instead of calling `Try.__init__()` directly.

    Args:
        thunk (Thunk[A]): the computation

    Returns:
        Try[A]: the resulting `Try`

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError(
            'mtry(%s) requires a thunk as an argument!' % thunk)
    try:
        return Success(thunk())
    except Exception as ex:
        return Failure(ex)


# noinspection PyMissingConstructor
class Success(Try[A]):
    def __init__(self, value: A):
        self._value: A = value

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of monad
        """
        return 'Success(%s)' % repr(self.get())

    def get(self) -> A:
        """
        Returns the inner value of the `Success[A]`.

        Returns:
            A: the inner value
        """
        return self._value


def success(value: A) -> Success[A]:
    """
    Injects a value into the `Success` monad.

    Args:
        value (A): the value

    Returns:
        Success[A]: the resulting monad
    """
    return Success(value)


# noinspection PyMissingConstructor
class Failure(Try):
    def __init__(self, ex: Exception):
        self._value: Exception = ex

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the monad
        """
        return 'Failure(%s)' % repr(self.get())

    def get(self) -> Exception:
        """
        Returns the `Failure`'s inner value.

        Returns:
            Exception: the inner value
        """
        return self._value

    def raise_ex(self):
        """
        Raises this `Failure` instance's exception.

        Raises:
            Exception: the exception
        """
        raise self.get()


def failure(ex: Exception) -> Failure:
    """
    Injects an exception into the `Failure` monad.

    Args:
        ex (Exception): the exception

    Returns:
        Failure: the resulting `Failure`
    """
    return Failure(ex)


def main():
    from genmonads.syntax import mfor

    print(mtry(lambda: 2)
          .flat_map(lambda x: mtry(lambda: 5)
                    .map(lambda y: x + y)))

    print(mfor(x + y
               for x in mtry(lambda: 2)
               for y in mtry(lambda: 5)))

    def make_gen():
        for x in mtry(lambda: 4):
            for y in mtry(lambda: 10):
                yield x - y

    print(mfor(make_gen()))

    print((mtry(lambda: 5) >> mtry(lambda: 2)))
    print(mtry(lambda: 1 / 0).map(lambda x: x * 2))
    print(mtry(lambda: 1 / 0).or_else(Success(0)))
    print(mtry(lambda: 1 / 0).recover(lambda _: 0))
    print(mtry(lambda: 1 / 0).recover_with(lambda _: Success(0)))


if __name__ == '__main__':
    main()
