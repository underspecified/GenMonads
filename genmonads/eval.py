from functools import reduce

from genmonads.monad import *
from genmonads.mtry import *
from genmonads.tailrec import *
from genmonads.util import *

__all__ = ['Eval', 'always', 'later', 'now']


class Eval(Monad):
    """
    A monad that represents computations. It consists of the following type classes:
    
    `Now[T]`: eager computations that are evaluated on creation.
    `Later[T]`: lazy computations that are evaluated once their value is requested.
    `Always[T]`: lazy computations that are evaluated every time their value is requested.

    Instances of `Eval[T]` are constructed by passing a computation wrapped in a thunk (i.e. a lambda expression
    with no arguments) to the `Eval.pure()`, `now()`, `later()`, or `always()` functions. The value of evaluating
    that computation can be retrieved via the `Eval.get()` function.
    
    Monadic computing is supported with `map()`, `flat_map()`, and `flatten()` functions, and for-comprehensions
    can be formed by evaluating generators over monads with the `mfor()` function. `Eval.flat_map()` is implemented
    tail-recursively with trampolines and supports infinite nesting.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Eval.
            Use the Eval.now(), Eval.later(), and Eval.always() functions instead."""
        )

    def __eq__(self, other):
        """
        Args:
            other (Eval[T]): the value to compare against

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
        return 'Eval'

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def flat_map(self, f):
        """
        Applies a function to the inner value of a `Eval`.

        Args:
            f (Callable[[B],Eval[C]): the function to apply

        Returns:
            Eval[C]: the resulting monad
        """
        if self.is_compute():
            return Compute(self.start, lambda s: Compute(lambda: self.run(s), f))
        elif self.is_call():
            return Compute(c._thunk, f)
        else:
            return Compute(lambda: self, f)

    def get(self):
        """
        Returns the Eval's inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        raise NotImplementedError

    def is_always(self):
        """
        Returns:
            bool: True if `self` is instance of `Always`, False otherwise
        """
        return type(self) == Always

    def is_call(self):
        """
        Returns:
            bool: True if `self` is instance of `Call`, False otherwise
        """
        return type(self) == Call

    def is_compute(self):
        """
        Returns:
            bool: True if `self` is instance of `Compute`, False otherwise
        """
        return type(self) == Compute

    def is_later(self):
        """
        Returns:
            bool: True if `self` is instance of `Later`, False otherwise
        """
        return type(self) == Later

    def is_now(self):
        """
        Returns:
            bool: True if `self` is instance of `Now`, False otherwise
        """
        return type(self) == Now

    def map(self, f):
        """
        Applies a function to the inner value of a `Eval`.

        Args:
            f (Callable[[B],Eval[C]): the function to apply

        Returns:
            Eval[C]: the resulting monad
        """
        return self.flat_map(lambda x: Now(f(x)))

    def memoize(self):
        """
        Memoize this instance of `Eval`. Will convert `Always` into a `Later` instance.

        Returns:
            Eval[T]: a memoized version of `self`. 
        """
        raise NotImplementedError

    @staticmethod
    def now(value):
        """
        Injects a value into the eager evaluation `Eval.Now` monad.

        This function should be used instead of calling `Eval.__init__()` directly.

        Args:
            value (T): the value

        Returns:
            Now[T]: the resulting `Eval`

        Raises:
            ValueError: if the argument is not a zero arity lambda function
        """
        return Now(value)

    @staticmethod
    def pure(value):
        """
        Injects a value into the `Eval` monad.

        This function should be used instead of calling `Eval.__init__()` directly.

        Args:
            value (T): the value

        Returns:
            Eval[T]: the resulting `Eval`
        """
        return Now(value)

    def to_mtry(self):
        return mtry(lambda: self.get())

    def to_option(self):
        return self.to_mtry().to_option()


# noinspection PyMissingConstructor
class Now(Eval):
    """
    A monad representing an eager computation that is evaluated once and memoized.
    """

    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return 'Now(%s)' % self.get()

    def get(self):
        return self._value

    def memoize(self):
        return self


def now(x):
    """
    Eagerly evaluates a value in the `Eval` monad.

    This function should be used instead of calling `Eval.__init__()` directly.

    Args:
        x (Union[T,Callable[[None],T]]): a value or computation

    Returns:
        Now[T]: the resulting `Now`
    """
    if is_thunk(x):
        return Now(x())
    else:
        return Now(x)


# noinspection PyMissingConstructor
class Later(Eval):
    """
    A monad representing a lazy computation that is evaluated once and memoized.
    
    It is roughly equivalent to a lazy value in languages like Scala and Haskell.
    Upon its evaluation, the closure containing the computation will be cleared.
    """

    def __init__(self, thunk):
        self._thunk = thunk
        self._value = None

    def __eq__(self, other):
        """
        Args:
            other (Later[T]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent, `False` otherwise
        """
        if type(self) == type(other):
            return (self._thunk, self._value) == (other._thunk, other._value)
        else:
            return False

    def __repr__(self):
        return 'Later(%s)' % str('<thunk>' if self._value is None else self.get())

    def get(self):
        if self._value is None:
            self._value = self._thunk()
            self._thunk = None  # clear the closure after evaluation
        return self._value

    def memoize(self):
        return self


def later(thunk):
    """
    Lazily evaluates a computation in the `Eval` monad.

    This function should be used instead of calling `Eval.__init__()` directly.

    Args:
        thunk (Callable[[None],T]): the computation

    Returns:
        Later[T]: the resulting `Later`

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError('Later(%s) requires a thunk as an argument!' % thunk)
    else:
        return Later(thunk)


# noinspection PyMissingConstructor
class Always(Eval):
    """
    A monad representing a lazy computation that is evaluated every time its result is requested.
    """

    def __init__(self, thunk):
        self._thunk = thunk

    def __eq__(self, other):
        """
        Args:
            other (Always[T]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent, `False` otherwise
        """
        if type(self) == type(other):
            return self._thunk == other._thunk
        else:
            return False

    def __repr__(self):
        return 'Always(<thunk>)'

    def get(self):
        return self._thunk()

    def memoize(self):
        return Later(self._thunk)


def always(thunk):
    """
    Repeatedly evaluates a computation in the `Eval` monad.

    This function should be used instead of calling `Eval.__init__()` directly.

    Args:
        thunk (Callable[[None],T]): the computation

    Returns:
        Always[T]: the resulting `Always`

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError('Always(%s) requires a thunk as an argument!' % thunk)
    else:
        return Always(thunk)


# noinspection PyMissingConstructor
class Call(Eval):
    """
    A monad representing a lazy computation that is evaluated once and memoized.

    It is roughly equivalent to a lazy value in languages like Scala and Haskell.
    Upon its evaluation, the closure containing the computation will be cleared.
    """

    def __init__(self, thunk):
        self._thunk = thunk

    def __eq__(self, other):
        """
        Args:
            other (Call[T]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent, `False` otherwise
        """
        if type(self) == type(other):
            return self._thunk == other._thunk
        else:
            return False

    def __repr__(self):
        return 'Call(<thunk>)'

    @staticmethod
    def _loop(fa):
        # noinspection PyProtectedMember
        def go(_fa):
            if _fa.is_call():
                return lambda: go(_fa._thunk()),
            elif _fa.is_compute():
                return Compute(lambda: _fa.start(), lambda s: Call._loop1(_fa.run(s))),
            else:
                return _fa

        return trampoline(go, fa)

    @staticmethod
    def _loop1(fa):
        return Call._loop(fa)

    def get(self):
        return Call._loop(self).get()

    def memoize(self):
        return Later(lambda: self.get())


def defer(thunk):
    """
    Defer a computation that produces an `Eval` monad.

    This function should be used instead of calling `Eval.__init__()` directly.

    Args:
        thunk (Callable[[None],Eval[T]]): the computation

    Returns:
        Eval[T]: an `Eval` that will contain the value of the computation once evaluated

    Raises:
        ValueError: if the argument is not a zero arity lambda function
    """
    if not is_thunk(thunk):
        raise ValueError('defer() requires a thunk as an argument!' % thunk)
    else:
        return Call(thunk)


# noinspection PyMissingConstructor
class Compute(Eval):
    def __init__(self, start, run):
        self.start = start
        self.run = run
        self._value = None

    def __eq__(self, other):
        """
        Args:
            other (Compute[T]): the value to compare against

        Returns:
            bool: `True` if the thunks or inner values are equivalent, `False` otherwise
        """
        if type(self) == type(other):
            return (self.start, self.run, self._value) == (other.start, other.run, other._value)
        else:
            return False

    def __repr__(self):
        if self._value is None:
            return 'Compute(<thunk>)'
        else:
            return 'Compute(%s)' % self.get()

    def get(self):
        def go(curr, fs):
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

        if self._value is None:
            self._value = trampoline(go, self, [])
        return self._value

    def memoize(self):
        return Later(lambda: self.get())


def main():
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
                 range(1, n+1),
                 1))
    print(reduce(lambda x, y: x.flat_map(lambda xx: later(lambda: xx * y)),
                 range(1, n+1),
                 later(lambda: 1))
          .get())
    from genmonads.option import option
    print(reduce(lambda x, y: x.flat_map(lambda xx: option(xx * y)),
                 range(1, n+1),
                 option(1))
          .get())


if __name__ == '__main__':
    main()
