from genmonads.eval import Eval
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.mytypes import *
from genmonads.option_base import Option as OptionBase

__all__ = ['Nothing', 'Option', 'Some', 'nothing', 'option', 'some']


class Option(OptionBase[A],
             MonadFilter[A],
             Foldable[A]):
    """
    A type class that represents an optional value.

    Instances of type `Option[A]` are either an instance of `Some[A]` or
    `Nothing`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and
    `filter()` functions, and for-comprehensions can  be formed by evaluating
    generators over monads with the `mfor()` function.
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

    def fold_left(self, b: B, f: FoldLeft[B, A]) -> B:
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (Callable[[B, A], B]): the function to fold with

        Returns:
            B: the result of folding
        """
        return f(b, self.get()) if self.is_defined() else b

    def fold_right(self,
                   lb: 'Eval[B]',
                   f: FoldRight[A, 'Eval[B]']
                   ) -> 'Eval[B]':
        """
        Performs left-associated fold using `f`. Uses lazy evaluation,
        requiring type `Eval[B]` for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (Callable[[A,Eval[B]],Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        return f(self.get(), lb) if self.is_defined() else lb

    def get(self):
        """
        Returns the `Gettable`'s inner value.

        Returns:
            T: the inner value
        """
        raise NotImplementedError

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
