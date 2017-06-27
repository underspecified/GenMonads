from types import LambdaType
import inspect

from genmonads.monad import *
from genmonads.mtry import *
from genmonads.tailrec import *

__all__ = ['Eval', 'always', 'later', 'now']


def is_lambda(f):
    return isinstance(f, LambdaType)


def arity(f):
    sig = inspect.signature(f)
    return len(sig.parameters)


def is_thunk(f):
    return is_lambda(f) and arity(f) == 0


class Eval(Monad):
    """
    A type that represents a failable computation.

    Instances of type `Try[T]` are either instances of `Success[T]` or `Failure[T]`. This monad uses eager evaluation.
    For lazy computations, see the `Task` monad (under construction).

    Instances of `Try[T]` are constructed by passing a computation wrapped in a thunk (i.e. a lambda expression
    with no arguments) to either the `now()` or `Try.pure()` or functions. The thunk is evaluated immediately,
    and successful computations return the result wrapped in `Success`, while computations that raise an exception
    return that exception wrapped in `Failure[T]`.

    Monadic computing is supported with `map`, `flat_map()`, and `flatten()`, functions, and for-comprehensions
    can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Try.
            Use the Eval.now(), Eval.later(), and Eval.always() functions instead."""
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
        return 'Eval'

    # noinspection PyUnresolvedReferences,PyProtectedMember
    def flat_map(self, f):
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[B],Try[C]): the function to apply

        Returns:
            Try[C]: the resulting monad
        """
        if self.is_compute():
            return Compute(self.start, lambda s: Compute(lambda: self.run(s), f))
        elif self.is_call():
            return Compute(c._thunk, f)
        else:
            return Compute(lambda: self, f)

    def get(self):
        """
        Returns the Try's inner value.

        Returns:
            Union[T,Exception]: the inner value
        """
        raise NotImplementedError

    def is_always(self):
        return type(self) == Always

    def is_call(self):
        return type(self) == Call

    def is_compute(self):
        return type(self) == Compute

    def is_later(self):
        return type(self) == Later

    def is_now(self):
        return type(self) == Now

    def map(self, f):
        """
        Applies a function to the inner value of a `Try`.

        Args:
            f (Callable[[B],Try[C]): the function to apply

        Returns:
            Try[C]: the resulting monad
        """
        return self.flat_map(lambda x: Now(f(x)))

    def memoize(self):
        raise NotImplementedError

    @staticmethod
    def now(value):
        """
        Injects a value into the eager evaluation `Eval.Now` monad.

        This function should be used instead of calling `Eval.__init__()` directly.

        Args:
            value (T): the value

        Returns:
            Now[T]: the resulting `Try`

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
    def __init__(self, thunk):
        self._thunk = thunk
        self._value = None

    def __repr__(self):
        return 'Later(%s)' % self._thunk if self._value is None else self.get()

    def get(self):
        if self._value is None:
            self._value = self._thunk()
            self._thunk = None
        return self._value

    def memoize(self):
        return self


def later(thunk):
    """
    Lazily evaluates a value in the `Eval` monad.

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
    def __init__(self, thunk):
        self._thunk = thunk

    def __repr__(self):
        return 'Always(%s)' % self._thunk

    def get(self):
        return self._thunk()

    def memoize(self):
        return Later(self._thunk)


def always(thunk):
    """
    Repeatedly evaluates a value in the `Eval` monad.

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
    def __init__(self, thunk):
        self._thunk = thunk

    def __repr__(self):
        return 'Call(%s)' % self._thunk

    def get(self):
        return Call.loop(self).get()

    @staticmethod
    def loop(fa):
        # noinspection PyProtectedMember
        def go(_fa):
            if fa.is_call():
                return lambda: go(_fa._thunk()),
            elif fa.is_compute():
                return Compute(lambda: _fa.start(), lambda s: Call.loop(_fa.run(s))),
            else:
                return _fa

        return trampoline(go, fa)

    def memoize(self):
        return Later(lambda: self.get())


# noinspection PyMissingConstructor
class Compute(Eval):
    def __init__(self, start, run):
        self.start = start
        self.run = run
        self._value = None

    def __repr__(self):
        if self._value is None:
            return 'Compute(%s, %s)' % (self.start, self.run)
        else:
            return 'Compute(%s)' % self.get()

    def get(self):
        def go(curr, fs):
            if curr.is_compute():
                cc = curr.start()
                if cc.is_compute():
                    return lambda: go(cc, [cc.run, curr.run] + fs)
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

if __name__ == '__main__':
    main()
