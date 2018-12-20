from functools import reduce
import typing

from genmonads.monad import Monad
from genmonads.mytypes import *
from genmonads.option_base import Option, Some, Nothing
from genmonads.tailrec import trampoline
from genmonads.util import is_thunk


__all__ = ['Always', 'Eval', 'Later', 'Now', 'always', 'defer', 'later', 'now']


# noinspection PyMissingConstructor,PyUnresolvedReferences
class Eval(Monad,
           Generic[A]):
    """
    A monad that represents computations. It consists of the following type
    classes:
    
    `Now[T]`: eager computations that are evaluated on creation.
    `Later[T]`: lazy computations that are evaluated once their value is
    requested.
    `Always[T]`: lazy computations that are evaluated every time their value is
    requested.

    Instances of `Eval[T]` are constructed by passing a computation wrapped in
    a thunk (i.e. a lambda expression with no arguments) to the `Eval.pure()`,
    `now()`, `later()`, or `always()` functions. The value of evaluating that
    computation can be retrieved via the `Eval.get()` function.
    
    Monadic computing is supported with `map()`, `flat_map()`, and `flatten()`
    functions, and for-comprehensions can be formed by evaluating generators
    over monads with the `mfor()` function. `Eval.flat_map()` is implemented
    tail-recursively with trampolines and supports infinite nesting.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Eval.
            Use the Eval.now(), Eval.later(), and Eval.always() functions
            instead."""
        )

    def __eq__(self, other: 'Eval[B]') -> bool:
        """
        Args:
            other (Eval[B]): the value to compare against

        Returns:
            bool: `True` if inner values are equivalent, `False` otherwise
        """
        if type(self) == type(other):
            return self.get_or_none() == other.get_or_none()
        else:
            return False

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the name of the type class
        """
        return 'Eval'

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def flat_map(self, f: Callable[[B], 'Eval[C]']) -> 'Eval[C]':
        """
        Applies a function to the inner value of a `Eval`.

        Args:
            f (Callable[[B], Eval[C]]): the function to apply

        Returns:
            Eval[C]: the resulting monad
        """
        if self.is_compute():
            return Compute(self.start,
                           lambda s: Compute(lambda: self.run(s), f))
        elif self.is_call():
            return Compute(self._thunk, f)
        else:
            return Compute(lambda: self, f)

    def get(self) -> Union[T, Exception]:
        """
        Returns the Eval's inner value.

        Returns:
            Union[T, Exception]: the inner value
        """
        raise NotImplementedError

    def is_always(self) -> bool:
        """
        Returns:
            bool: True if `self` is instance of `Always`, False otherwise
        """
        return type(self) == Always

    def is_call(self) -> bool:
        """
        Returns:
            bool: True if `self` is instance of `Call`, False otherwise
        """
        return type(self) == Call

    def is_compute(self) -> bool:
        """
        Returns:
            bool: True if `self` is instance of `Compute`, False otherwise
        """
        return type(self) == Compute

    def is_later(self) -> bool:
        """
        Returns:
            bool: True if `self` is instance of `Later`, False otherwise
        """
        return type(self) == Later

    def is_now(self) -> bool:
        """
        Returns:
            bool: True if `self` is instance of `Now`, False otherwise
        """
        return type(self) == Now

    def map(self, f: Callable[[B], 'Eval[C]']) -> 'Eval[C]':
        """
        Applies a function to the inner value of a `Eval`.

        Args:
            f (Callable[[B], Eval[C]]): the function to apply

        Returns:
            Eval[C]: the resulting monad
        """
        return self.flat_map(lambda x: Now(f(x)))

    def memoize(self) -> 'Eval[A]':
        """
        Memoize this instance of `Eval`. Will convert `Always` into a `Later`
        instance.

        Returns:
            Eval[A]: a memoized version of `self`.
        """
        raise NotImplementedError

    @staticmethod
    def now(value: A) -> 'Now[A]':
        """
        Injects a value into the eager evaluation `Eval.Now` monad.

        This function should be used instead of calling `Eval.__init__()`
        directly.

        Args:
            value (A): the value

        Returns:
            Now[A]: the resulting `Eval`

        Raises:
            ValueError: if the argument is not a zero arity lambda function
        """
        return Now(value)

    @staticmethod
    def pure(value: A) -> 'Eval[A]':
        """
        Injects a value into the `Eval` monad.

        This function should be used instead of calling `Eval.__init__()`
        directly.

        Args:
            value (A): the value

        Returns:
            Eval[A]: the resulting `Eval`
        """
        return Now(value)

    def to_mtry(self) -> 'Try[A]':
        from genmonads.mtry import mtry
        return mtry(lambda: self.get())

    def to_option(self) -> 'Option[A]':
        return self.to_mtry().to_option()


# noinspection PyMissingConstructor
class Now(Eval[A]):
    """
    A monad representing an eager computation that is evaluated once and
    memoized.
    """

    def __init__(self, value: A):
        self._value = value

    def __repr__(self) -> str:
        return 'Now(%s)' % self.get()

    def get(self) -> A:
        return self._value

    def memoize(self) -> 'Now[A]':
        return self


def now(x: Union[A, Thunk[A]]) -> 'Now[A]':
    """
    Eagerly evaluates a value in the `Eval` monad.

    This function should be used instead of calling `Eval.__init__()`
    directly.

    Args:
        x (Union[A, Callable[[], A]]): a value or computation

    Returns:
        Now[T]: the resulting `Now`
    """
    if is_thunk(x):
        return Now(x())
    else:
        return Now(x)


# noinspection PyMissingConstructor
class Later(Eval[A]):
    """
    A monad representing a lazy computation that is evaluated once and memoized.
    
    It is roughly equivalent to a lazy value in languages like Scala and Haskell.
    Upon its evaluation, the closure containing the computation will be cleared.
    """

    def __init__(self, thunk: Thunk[A]):
        self._thunk: Thunk[A] = thunk
        self._value: Some[A] = Nothing()

    def __eq__(self, other: 'Later[A]') -> bool:
        """
        Args:
            other (Later[A]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent, `False`
            otherwise
        """
        return (type(self) == type(other) and
                (self._thunk, self._value) == (other._thunk, other._value))

    def __repr__(self) -> str:
        return 'Later(%s)' % self._value.get_or_else('<thunk>')

    def get(self) -> A:
        if self._value.is_empty():
            self._value = Some(self._thunk())
            self._thunk = None  # clear the closure after evaluation
        return self._value.get()

    def memoize(self) -> 'Later[A]':
        return self


def later(thunk: Thunk[A]) -> Later[A]:
    """
    Lazily evaluates a computation in the `Eval` monad.

    This function should be used instead of calling `Eval.__init__()` directly.

    Args:
        thunk (Thunk[A]): the computation

    Returns:
        Later[A]: the resulting `Later`

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError('Later(%s) requires a thunk as an argument!' % thunk)
    else:
        return Later(thunk)


# noinspection PyMissingConstructor
class Always(Eval[A]):
    """
    A monad representing a lazy computation that is evaluated every time its
    result is requested.
    """

    def __init__(self, thunk: Thunk[A]):
        self._thunk = thunk

    def __eq__(self, other: 'Always[A]') -> bool:
        """
        Args:
            other (Always[A]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent,
            `False` otherwise
        """
        if type(self) == type(other):
            return self._thunk == other._thunk
        else:
            return False

    def __repr__(self) -> str:
        return 'Always(<thunk>)'

    def get(self) -> A:
        return self._thunk()

    def memoize(self) -> Later[A]:
        return Later(self._thunk)


def always(thunk: Thunk[A]) -> Always[A]:
    """
    Repeatedly evaluates a computation in the `Eval` monad.

    This function should be used instead of calling `Eval.__init__()` directly.

    Args:
        thunk (Thunk[A]): the computation

    Returns:
        Always[A]: the resulting `Always`

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError('Always(%s) requires a thunk as an argument!' % thunk)
    else:
        return Always(thunk)


# noinspection PyMissingConstructor
class Call(Eval[A]):
    """
    A monad representing a lazy computation that is evaluated once and memoized.

    It is roughly equivalent to a lazy value in languages like Scala and Haskell.
    Upon its evaluation, the closure containing the computation will be cleared.
    """

    def __init__(self, thunk: Thunk[A]):
        self._thunk = thunk

    def __eq__(self, other: 'Call[A]'):
        """
        Args:
            other (Call[A]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent,
            `False` otherwise
        """
        if type(self) == type(other):
            return self._thunk == other._thunk
        else:
            return False

    def __repr__(self) -> str:
        return 'Call(<thunk>)'

    @staticmethod
    def _loop(fa: 'Call[A]') -> 'Call[A]':
        # noinspection PyProtectedMember
        def go(_fa: Union['Call[A]', 'Compute[A]', Thunk[A]]
               ) -> Union['Call[A]', 'Compute[A]', Thunk[A]]:
            if _fa.is_call():
                return lambda: go(_fa._thunk())
            elif _fa.is_compute():
                return Compute(
                    lambda: _fa.start(),
                    lambda s: Call._loop1(_fa.run(s))
                )
            else:
                return _fa

        return trampoline(go, fa)

    @staticmethod
    def _loop1(fa: 'Call[A]') -> 'Call[A]':
        return Call._loop(fa)

    def get(self) -> A:
        return Call._loop(self).get()

    def memoize(self) -> 'Later[A]':
        return Later(lambda: self.get())


def defer(thunk: Thunk[A]) -> 'Eval[A]':
    """
    Defer a computation that produces an `Eval` monad.

    This function should be used instead of calling `Eval.__init__()` directly.

    Args:
        thunk (Thunk[A]): the computation

    Returns:
        Eval[A]: an `Eval` that will contain the value of the computation once
                 evaluated

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError('defer() requires a thunk as an argument!' % thunk)
    else:
        return Call(thunk)


# noinspection PyMissingConstructor
class Compute(Eval[A]):
    def __init__(self, start, run):
        self.start = start
        self.run = run
        self._value = Nothing()

    def __eq__(self, other: 'Compute[A]') -> bool:
        """
        Args:
            other (Compute[A]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent,
                  `False` otherwise
        """
        if type(self) == type(other):
            return (self.start, self.run, self._value) == \
                   (other.start, other.run, other._value)
        else:
            return False

    def __repr__(self) -> str:
        return 'Compute(%s)' % self._value.get_or_else('<thunk>')

    def get(self) -> A:
        def go(curr: Union['Compute[A]', Thunk[A]],
               fs: typing.List[F1[A, Call[A]]]
               ) -> Union[A,
                          Tuple[Union['Compute[A]', typing.List[Thunk[A]],
                                      typing.List[F1[A, Call[A]]]]]]:
            if curr.is_compute():
                cc = curr.start()
                if cc.is_compute():
                    return lambda: go(cc.start(), [cc.run, curr.run] + fs)
                else:
                    return lambda: go(curr.run(cc.get()), fs)
            elif fs:
                f, *rest = fs
                return lambda: go(f(curr.get()), rest)
            else:
                return curr.get()

        if self._value.is_empty():
            # noinspection PyAttributeOutsideInit
            self._value = Some(trampoline(go, self, []))
        return self._value.get_or_none()

    def memoize(self) -> 'Later[A]':
        return Later(lambda: self.get())


def main():
    from genmonads.syntax import mfor

    print(now(2))
    print(now(lambda: 3))

    print(now(2)
          .flat_map(lambda x: later(lambda: 5)
                    .map(lambda y: x + y))
          .get())

    print(mfor(x + y
               for x in later(lambda: 2)
               for y in later(lambda: 5))
          .get())

    def make_gen():
        for x in later(lambda: 4):
            for y in later(lambda: 10):
                yield x - y

    print(mfor(make_gen()).get())

    print((later(lambda: 5) >> later(lambda: 2))
          .get())
    # noinspection PyUnresolvedReferences
    print(later(lambda: 1 / 0)
          .map(lambda x: x * 2)
          .to_mtry())

    n = 1000
    print(reduce(lambda x, y: x * y,
                 range(1, n + 1),
                 1))
    print(reduce(lambda x, y: x.flat_map(lambda xx: later(lambda: xx * y)),
                 range(1, n + 1),
                 later(lambda: 1))
          .get())

    from genmonads.option import option
    print(reduce(lambda x, y: x.flat_map(lambda xx: option(xx * y)),
                 range(1, n + 1),
                 option(1))
          .get())


if __name__ == '__main__':
    main()
