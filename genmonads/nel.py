import typing

from genmonads.convertible import Convertible
from genmonads.either import Either
from genmonads.eval import Eval
from genmonads.foldable import Foldable
from genmonads.mlist import List as MList, Nil
from genmonads.monadfilter import MonadFilter
from genmonads.mtry_base import mtry
from genmonads.mytypes import *
from genmonads.option_base import Some, Option
from genmonads.tailrec import trampoline

__all__ = ['NonEmptyList', 'nel', 'onel']


class NonEmptyList(MonadFilter[A],
                   Foldable[A],
                   Convertible[A]):
    """
    A type that represents a non-empty list of a single type.

    Monadic computing is supported with `map()` and `flat_map()` functions,
    and for-comprehensions can be formed by evaluating generators over monads
    with the `mfor()` function.
    """

    def __init__(self, head: A, *tail: A):
        if not head:
            raise ValueError('Tried to construct an empty NonEmptyList!')
        self.head: A = head
        self.tail: typing.List[A] = list(tail)
        self._value: typing.List[A] = [self.head, ] + self.tail

    def __bool__(self) -> bool:
        """
        Returns:
            bool: True; `NonEmptyList` are never empty
        """
        return True

    def __eq__(self, other: 'NonEmptyList[A]') -> bool:
        """
        Args:
            other (NonEmptyList[A]): the value to compare against

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
        return 'NonEmptyList'

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the List
        """
        return 'NonEmptyList(%s)' % ', '.join(repr(v) for v in self.get())

    # noinspection PyTypeChecker
    @staticmethod
    def empty() -> MList[A]:
        return Nil

    def filter(self,
               p: Predicate[A]
               ) -> MList[A]:
        """
        Filters this monad by applying the predicate `f` to the monad's inner
        value.
        Returns this monad if the predicate is `True`, this monad's empty
        instance otherwise.

        Args:
            p (Predicate[A]): the predicate

        Returns:
            Union[MList[A],
                  NonEmptyList[A]]: a list containing all inner values where
                                    the predicate is `True`
        """
        return self.to_mlist().filter(p)

    def flat_map(self, f: F1[A, 'NonEmptyList[B]']) -> 'NonEmptyList[B]':
        """
        Applies a function that produces a Monad's from unwrapped values to a
        Monad's inner value and flattens the nested result.

        If the inner values can be converted to an instance of `NonEmptyList`
        by having an implementation of `to_onel()`, the inner values will be
        converted to `NonEmptyList` before flattening. This allows for
        flattening of `NonEmptyList[Option[A]]` into `NonEmptyList[A]`, as is
        done in Scala.

        Args:
            f (Callable[[A],NonEmptyList[B]]): the function to apply

        Returns:
            NonEmptyList[B]: the resulting monad
        """
        def to_list(vs: Union[NonEmptyList[A], A]):
            """
            Args:
                vs (Union[NonEmptyList[A], A]): the values

            Returns:
                List[A]: the values as a list
            """
            return vs.to_mlist().get_or_else([vs, ])

        return NonEmptyList(*[v
                              for vs in (f(v1)for v1 in self.get())
                              for v in to_list(vs)])

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

    def fold_right(self, lb: Eval[B], f: FoldRight[A, Eval[B]]) -> Eval[B]:
        """
        Performs left-associated fold using `f`. Uses lazy evaluation,
        requiring type `Eval[B]` for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (FoldRight[A,Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        for a in reversed(self.get()):
            lb = f(a, lb)
        return lb

    def get(self) -> typing.List[A]:
        """
        Returns the `Nel`'s inner value.

        Returns:
            typing.List[A]: the inner value
        """
        return self._value

    def last(self) -> A:
        """
        Returns the last item in the nel.

        Returns:
            A: the last item
        """
        return self.get()[-1]

    def map(self, f: F1[A, B]) -> 'NonEmptyList[B]':
        """
        Applies a function to the inner value of a nel.

        Args:
            f (F1[A, B]): the function to apply

        Returns:
            NonEmptyList[B]: the resulting NonEmptyList
        """
        return NonEmptyList(*(f(v) for v in self.get()))

    def mtail(self) -> 'MList[A]':
        """
        Returns the tail of the nel as a monadic List.

        Returns:
            List[A]: the rest of the nel
        """
        return MList.pure(*self.tail)

    @staticmethod
    def pure(*values: A) -> 'NonEmptyList[A]':
        """
        Injects a value into the `NonEmptyList` monad.

        Args:
            values (A): the values

        Returns:
            NonEmptyList[A]: the resulting `NonEmptyList`
        """
        return NonEmptyList(*values)

    # noinspection PyPep8Naming
    @staticmethod
    def tailrecM(f: F1[A, 'NonEmptyList[Either[A, B]]'],
                 a: A
                 ) -> 'NonEmptyList[B]':
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (F1[A, NonEmptyList[Either[A, B]]]): the function to apply
            a: the recursive function's input

        Returns:
            NonEmptyList[B]: a Nel containing the result of applying the
                             tail-recursive function to its argument
        """

        def go(a1):
            fa = f(a1)
            e = fa.head
            a2 = e.get()
            return fa.pure(a2) if e.is_right() else lambda: go(a2)

        return trampoline(go, a)

    def to_iter(self) -> typing.Iterator[A]:
        """
        Converts the `NonEmptyList` into a python miter.

        Returns:
            typing.Iterator[A]: the resulting python miter
        """
        return (x for x in self.get())

    def to_list(self) -> typing.List[A]:
        """
        Converts the `NonEmptyList` into a python list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return self.get()

    def to_nel(self) -> 'NonEmptyList[A]':
        """
        Converts the NonEmptyList into a NonEmptyList.

        Returns:
            NonEmptyList: the resulting NonEmptyList
        """
        return self

    def to_onel(self) -> 'Option[NonEmptyList[A]]':
        """
        Converts the NonEmptyList into a NonEmptyList wrapped in Option.

        Returns:
            Option[NonEmptyList[A]]: the resulting NonEmptyList
        """
        return Some(self)

    def unpack(self) -> Tuple[A, ...]:
        """
        Returns the inner value as a tuple to support unpacking

        Returns:
            Tuple[A]: the inner values as a tuple
        """
        return tuple(self.get())


# noinspection PyUnresolvedReferences
def onel(*values: A) -> 'Option[NonEmptyList[A]]':
    """
    Constructs a `NonEmptyList` instance from a tuple of values.

    Args:
        values (A): the values

    Returns:
        Option[NonEmptyList[A]]: the resulting `NonEmptyList` wrapped in `Some`
                                 if the argument list is non-empty, `Nothing`
                                 otherwise
    """
    return mtry(lambda: NonEmptyList.pure(*values)).to_option()


# noinspection PyUnresolvedReferences
def nel(*values: A) -> 'NonEmptyList[A]':
    """
    Constructs a `NonEmptyList` instance from a tuple of values.

    Args:
        values (A): the values

    Returns:
        NonEmptyList[A]: the resulting `NonEmptyList`
    """
    return NonEmptyList.pure(*values)


def main():
    from genmonads.syntax import mfor
    from genmonads.mtry import mtry

    print(nel(2, 3).flat_map(lambda x: nel(x + 5)))

    print(mfor(x + y
               for x in nel(2, 4, 6)
               for y in nel(5, 7, 9)))

    def make_gen():
        for x in nel(4):
            for y in nel(10):
                yield x - y

    print(mfor(make_gen()))

    print(nel(5) >> (lambda x: nel(x * 2)))

    print(mtry(lambda: nel().map(lambda x: x * 2)))

    print(mtry(lambda: 1/0).to_option())

    #print(onel().map(lambda x: x * 2))

    #print(nel(nel(1, 2, 3, 4, 5), nel(5, 4, 3, 2, 1)).flatten())


if __name__ == '__main__':
    main()
