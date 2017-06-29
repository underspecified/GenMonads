from genmonads.util import is_thunk

from genmonads.foldable import Foldable
from genmonads.monad import Monad

__all__ = ['Failure', 'Success', 'Try', 'failure', 'mtry', 'success']


class Try(Foldable, Monad):
    """
    A type that represents a failable computation.

    Instances of type `Try[T]` are either instances of `Success[T]` or `Failure[T]`. This monad uses eager evaluation.
    For lazy computations, see the `Task` monad (under construction).

    Instances of `Try[T]` are constructed by passing a computation wrapped in a thunk (i.e. a lambda expression
    with no arguments) to either the `mtry()` or `Try.pure()` or functions. The thunk is evaluated immediately,
    and successful computations return the result wrapped in `Success`, while computations that raise an exception
    return that exception wrapped in `Failure[T]`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions, and
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
        return 'Try'

    def cata(self, fa, fb):
        """
        Transforms an `Either[A,B]` instance by applying `fa` to the inner value of instances of Left[A],
        and `fb` to the inner value of instance of Right[B].

        Args:
            fa (Callable[[A],C): the function to apply to instances of `Left[A]`
            fb (Callable[[B],C): the function to apply to instances of `Right[B]`

        Returns:
            C: the resulting `C` instance
        """
        return fb(self.get()) if self.is_success() else fa(self.get())

    @staticmethod
    def empty():
        """
        Returns:
            Try[T]: `Failure[T]` with a `ValueError`, the empty instance for this `MonadFilter`
        """
        return Failure(ValueError("This Try instance is empty!"))

    def flat_map(self, f):
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[B],Try[C]): the function to apply

        Returns:
            Try[C]: the resulting monad
        """
        return f(self.get()) if self.is_success() else self

    def fold_left(self, b, f):
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (Callable[[B,A],B]): the function to fold with

        Returns:
            B: the result of folding
        """
        return f(b, self.get()) if self.is_success() else b

    def fold_right(self, lb, f):
        """
        Performs left-associated fold using `f`. Uses lazy evaluation, requiring type `Eval[B]`
        for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (Callable[[A,Eval[B]],Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        return f(self.get(), lb) if self.is_success() else lb

    def get(self):
        """
        Returns the Try's inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        raise NotImplementedError

    def is_failure(self):
        return isinstance(self, Failure)

    def is_success(self):
        return isinstance(self, Success)

    def or_else(self, default):
        """
        Returns the `Try` if an instance of `Success` or `default` if an instance of `Failure` .

        Args:
            default (Try[B]): the monad to return for `Failure[T]` instances

        Returns:
            Try[B]: the resulting `Try`
        """
        return self if self.is_success() else default

    @staticmethod
    def pure(value):
        """
        Injects a value into the `Try` monad.

        This function should be used instead of calling `Try.__init__()` directly.

        Args:
            value (T): the value

        Returns:
            Try[T]: the resulting `Try`
            
        Raises:
            ValueError: if the argument is not a zero arity lambda function
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
        return self if self.is_success() else f(self.get())

    def recover_with(self, f):
        """
        Recovers from a failed computation by applying `f` to the `Failure[T]` instance.

        Essentially, a flat_map on the `Failure` instance.

        Args:
            f (Callable[[Exception],Try[B]): the function to call on the `Failure[T]`

        Returns:
            Try[B]: the resulting `Try`
        """
        return self if self.is_success() else f(self)

    def to_option(self):
        """
        Converts an instance of `Try[T]` to `Option[T]`.

        `Success[T]` is mapped to `Some[T]`, and `Failure[T]` is mapped to `Nothing[T]`.

        Returns:
            Option[T]: the corresponding `Option`
        """
        from genmonads.option import Some
        return Some(self.get()) if self.is_success() else None


def mtry(thunk):
    """
    Evaluates a failable computation in the `Try` monad.

    This function should be used instead of calling `Try.__init__()` directly.

    Args:
        thunk (Callable[[None],T]): the computation

    Returns:
        Try[T]: the resulting `Try`

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError('Try.pure(%s) requires a thunk as an argument!' % thunk)
    try:
        return Success(thunk())
    except Exception as ex:
        return Failure(ex)


# noinspection PyMissingConstructor
class Success(Try):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        """
        Returns:
            str: a string representation of monad
        """
        return 'Success(%s)' % repr(self.get())

    def get(self):
        """
        Returns the `Try`'s inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        return self._value


def success(value):
    """
    Injects a value into the `Success` monad.

    Args:
        value (T): the value

    Returns:
        Try[T]: the resulting monad
    """
    return Success(value)


# noinspection PyMissingConstructor
class Failure(Try):
    def __init__(self, ex):
        self._value = ex

    def __repr__(self):
        """
        Returns:
            str: a string representation of the monad
        """
        return 'Failure(%s)' % repr(self.get())

    def get(self):
        """
        Returns the `Try`'s inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        return self._value

    def raise_ex(self):
        """
        Raises this `Failure` instance's exception.

        Raises:
            Exception: the exception
        """
        raise self.get()


def failure(ex):
    """
    Injects an exception into the `Failure` monad.

    Args:
        ex (Exception): the exception

    Returns:
        Failure[T]: the resulting `Failure`
    """
    return Failure(ex)


def main():
    from genmonads.monad import mfor

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
