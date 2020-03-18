
from genmonads.eval import Eval
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.mtry_base import Try as TryBase
from genmonads.mytypes import *
from genmonads.util import is_thunk

__all__ = ['Failure', 'Success', 'Try', 'failure', 'mtry', 'success']


class Try(TryBase[A],
          MonadFilter[A],
          Foldable[A]):
    """
    A type that represents a failable computation.

    Instances of type `Try[A]` are either instances of `Success[A]` or
    `Failure[A]`.
    This monad uses eager evaluation. For lazy computations, see the `Eval`
    monad.

    Instances of `Try[A]` are constructed by passing a computation wrapped in
    a thunk (i.e. a lambda expression with no arguments) to either the `mtry()`
    or `Try.pure()` or functions. The thunk is evaluated immediately, and
    successful computations return the result wrapped in `Success`, while
    computations that raise an exception return that exception wrapped in
    `Failure[A]`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`,
    and `filter()` functions, and for-comprehensions can be formed by
    evaluating generators over monads with the `mfor()` function.
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

    def fold_left(self, b: B, f: FoldLeft[B, A]) -> B:
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (FoldLeft[B, A]): the function to fold with

        Returns:
            B: the result of folding
        """
        return f(b, self.get()) if self.is_success() else b

    def fold_right(self,
                   lb: 'Eval[B]',
                   f: FoldRight[A, 'Eval[B]']
                   ) -> 'Eval[B]':
        """
        Performs left-associated fold using `f`. Uses lazy evaluation,
        requiring type `Eval[B]` for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (FoldRight[A, Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        return f(self.get(), lb) if self.is_success() else lb

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

    print(mtry(lambda: 5) >> mtry(lambda: 2))
    print(mtry(lambda: 5).filter(lambda x: x % 2 == 0))
    print(mtry(lambda: 5).filter(lambda x: x % 2 != 0))
    print(mtry(lambda: 1 / 0).map(lambda x: x * 2))
    print(mtry(lambda: 1 / 0).or_else(Success(0)))
    print(mtry(lambda: 1 / 0).recover(lambda _: 0))
    print(mtry(lambda: 1 / 0).recover_with(lambda _: Success(0)))
    print(mtry(lambda: 1 / 0).to_list())
    print(mtry(lambda: 1 / 0).to_option())


if __name__ == '__main__':
    main()
