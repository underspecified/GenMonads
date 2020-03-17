import sys
import typing

from genmonads.convertible import Convertible
from genmonads.either import Either
from genmonads.eval import Eval
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.mtry import mtry
from genmonads.mytypes import *
from genmonads.option_base import Option
from genmonads.tailrec import trampoline

__all__ = ['List', 'Nil', 'mlist', 'nil']


class List(MonadFilter[A],
           Foldable[A],
           Convertible[A]):
    """
    A type that represents list of values of the same type.

    Instances are either of type `List[A]` or `Nil`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and
    `filter()` functions, and for-comprehensions can be formed by evaluating
    generators over monads with the `mfor()` function.
    """

    def __init__(self, *values: A):
        self._value: typing.List[A] = list(values)

    def __eq__(self, other: 'List[A]') -> bool:
        """
        Args:
            other (List[A]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `List` and inner values are
             equivalent, `False` otherwise
        """
        return (type(self) == type(other)
                and self.get_or_none() == other.get_or_none())

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the monad's name
        """
        return 'List'

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the List
        """
        return 'List(%s)' % ', '.join(repr(v) for v in self.get())

    @staticmethod
    def empty() -> 'Nil':
        """
        Returns:
            List[A]: `Nil`, the empty instance for this `MonadFilter`
        """
        return Nil()

    def flat_map(self, f: F1[A, 'List[B]']) -> 'List[B]':
        """
        Applies a function that produces an Monad from unwrapped values to a
        Monad's inner value and flattens the nested result.

        If the inner values can be converted to an instance of `List` by having
        an implementation of to_mlist()`, the inner values will be converted to
        `List` before flattening. This allows for flattening of
        `List[Option[A]]` into `List[A]`, as is done in Scala.

        Args:
            f (F1[A, List[B]]): the function to apply

        Returns:
            List[B]: the resulting monad
        """
        from genmonads.mtry import mtry

        def to_mlist(v: Union[A, 'List[A]']):
            """
            Args:
                v (Union[A, List[A]): the value

            Returns:
                Iterator[A]: the empty instance for this `MonadFilter`
            """
            return (mtry(lambda: v.to_mlist().get())
                    .get_or_else((v,)))

        return List(*[v
                      for vs in (f(v1) for v1 in self.get())
                      for v in to_mlist(vs)])

    def fold_left(self, b: B, f: FoldLeft[B, A]) -> B:
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (FoldLeft[B, A]): the function to fold with

        Returns:
            B: the result of folding
        """
        for a in self.get():
            b = f(b, a)
        return b

    def fold_right(self, lb: 'Eval[B]', f: FoldRight[A, B]) -> 'Eval[B]':
        """
        Performs left-associated fold using `f`. Uses lazy evaluation,
        requiring type `Eval[B]` for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (FoldRight[A, B]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        for a in reversed(self.get()):
            lb = f(a, lb)
        return lb

    def get(self) -> typing.List[A]:
        """
        Returns the `List`'s inner value.

        Returns:
            typing.List[A]: the inner value
        """
        return self._value

    def head(self) -> A:
        """
        Returns the first item in the list.

        Returns:
            A: the first item

        Throws:
            IndexError: if the list is empty
        """
        return self.get()[0]

    def head_option(self) -> Option[A]:
        """
        Safely returns the first item in the list by wrapping the attempt in
        `Option`.

        Returns:
            Option[A]: the first item wrapped in `Some`, or `Nothing` if the
                       list is empty
        """
        return mtry(lambda: self.head()).to_option()

    # noinspection PyMethodMayBeStatic
    def is_gettable(self) -> bool:
        return True

    def last(self) -> A:
        """
        Returns the last item in the list.

        Returns:
            A: the last item

        Throws:
            IndexError: if the list is empty
        """
        return self.get()[-1]

    def last_option(self) -> Option[A]:
        """
        Safely returns the last item in the list by wrapping the attempt in
        `Option`.

        Returns:
            Option[A]: the first item wrapped in `Some`, or `Nothing` if the
                       list is empty
        """
        return mtry(lambda: self.last()).to_option()

    def mtail(self) -> 'List[A]':
        """
        Returns the tail of the list as a monadic List.

        Returns:
            List[A]: the rest of the list
        """
        return mtry(lambda: self.tail()).to_mlist()

    @staticmethod
    def pure(*values) -> 'List[A]':
        """
        Injects a value into the `List` monad.

        Args:
            values (A): the values

        Returns:
            List[A]: the resulting `List`
        """
        return List(*values) if values else Nil()

    def tail(self) -> typing.List[A]:
        """
        Returns the tail of the list.

        Returns:
            typing.List[A]: the tail of the list
        """
        return self.get()[1:]

    # noinspection PyPep8Naming
    @staticmethod
    def tailrecM(f: F1[A, 'List[Either[A, B]]'], a: A) -> 'List[B]':
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (F1[A, 'List[Either[A, B]]']): the function to apply
            a (A): the recursive function's input

        Returns:
            F[B]: an `F` instance containing the result of applying the
                  tail-recursive function to its argument
        """

        def go(a1: A) -> Union[A, 'List[A]']:
            fa = f(a1)
            e = fa.head()
            a2 = e.get()
            return fa.pure(a2) if e.is_right() else lambda: go(a2)

        return trampoline(go, a)

    def to_iter(self) -> typing.Iterator[A]:
        """
        Converts the `List` into a pythonic iterator.

        Returns:
            typing.Iterator[A]: the resulting pythonic iterator
        """
        return (x for x in self.get())

    def to_list(self) -> typing.List[A]:
        """
        Converts the `List` into a python list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return self.get()

    def unpack(self) -> Tuple[A, ...]:
        """
        Returns the inner value as a tuple to support unpacking

        Returns:
            Tuple[A]: the inner values as a tuple
        """
        return tuple(self.get())


def mlist(*values: A) -> 'List[A]':
    """
    Constructs a `List` instance from a tuple of values.

    Args:
        values (A): the values

    Returns:
        stream.List[A]: the resulting `List`
    """
    return List.pure(*values)


# noinspection PyMissingConstructor,PyPep8Naming
class Nil(List):
    """
    A type that represents the empty list.
    """

    # noinspection PyInitNewSignature
    def __init__(self):
        self._value: typing.List = []

    def __eq__(self, other: 'List[A]'):
        """
        Args:
            other (List[A]): the value to compare against

        Returns:
            bool: `True` if other is instance of `Nil`, `False` otherwise
        """
        return isinstance(other, Nil)

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the `List`
        """
        return 'Nil'


def nil() -> Nil:
    """
    Constructs a `Nil` instance.

    Returns:
        Nil: the resulting `Nil`
    """
    return Nil()


def main():
    from genmonads.syntax import mfor

    print(mlist(2, 3).flat_map(lambda x: List.pure(x + 5)))

    print(mfor(x + y
               for x in mlist(2, 4, 6)
               if x < 10
               for y in mlist(5, 7, 9)
               if y % 2 != 0))

    def make_gen():
        for x in mlist(4):
            if x > 2:
                for y in mlist(10):
                    if y % 2 == 0:
                        yield x - y

    print(mfor(make_gen()))

    print(mlist(5) >> (lambda x: mlist(x * 2)))

    print(nil().map(lambda x: x * 2))

    print(mlist(mlist(1, 2, 3, 4, 5), mlist(5, 4, 3, 2, 1))
          .flat_map(lambda x: x.last_option()))

    xs = [1, 2, 3]
    ys = sys.argv[1:]  # ['a', 'b', 'c']
    print(mfor((x, y)
               for x in mlist(*xs)
               for y in mlist(*ys)))


if __name__ == '__main__':
    main()
