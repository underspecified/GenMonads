import itertools
import typing

from genmonads.convertible import Convertible
from genmonads.either import Either
from genmonads.eval import Now, defer, Eval
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.mtry_base import mtry
from genmonads.mytypes import *
from genmonads.option import Option
from genmonads.tailrec import trampoline

__all__ = ['Iterator', 'iterator', 'Stream', 'stream']


class Iterator(MonadFilter[A],
               Foldable[A],
               Convertible[A],
               Container[typing.Iterator[A]]):
    """
    A type that represents a lazy iterator of values. Useful for representing
    python iterators and generators.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and
    `filter()` functions, and for-comprehensions can be formed by evaluating
    generators over monads with the `mfor()` function.
    """

    def __init__(self, it: 'Iterator[A]'):
        self._value = it

    # noinspection PyProtectedMember
    def __eq__(self, other: 'Iterator[A]'):
        """
        Args:
            other (Iterator[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Iterator` and inner values
                  are equivalent, `False` otherwise
        """
        return type(self) == type(other) and self._value == other._value

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the monad's name
        """
        return 'Iterator'

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the Iterator
        """
        return 'Iterator(%s)' % str(self._value)

    def drop(self, n: int) -> 'Iterator[A]':
        return Iterator.from_iterator(itertools.islice(self.get(),
                                                       start=n,
                                                       stop=None))

    def drop_while(self, p: Predicate[A]) -> 'Iterator[A]':
        return Iterator.from_iterator(itertools.dropwhile(p, self.get()))

    @staticmethod
    def empty() -> 'Iterator[A]':
        """
        Returns:
            Iterator[A]: the empty instance for this `MonadFilter`
        """
        return Iterator.from_iterator((x for x in []))

    def filter(self, p: Predicate[A]) -> 'Iterator[A]':
        return Iterator.from_iterator(filter(p, self.get()))

    def flat_map(self, f: F1[A, 'Iterator[B]']) -> 'Iterator[B]':
        """
        Applies a function that produces a iterator from unwrapped values to an
        iterator's inner value and flattens the nested result.

        Args:
            f (Callable[[A],Iterator[B]]): the function to apply

        Returns:
            Iterator[B]: the resulting iterator
        """

        # def to_list(v: Union['Monad[T]', T]) -> 'Iterator[T]':
        #     return (mtry(lambda: v.to_iterator().to_list())
        #             .get_or_else([v, ]))

        def unpack(v: 'Union[A, Convertible[A]]') -> typing.Iterator[A]:
            """
            Args:
                v (Union[A, Convertible[A]): the value

            Returns:
                Iterator[A]: the unpacked result
            """
            if isinstance(v, Iterator):
                return v._value
            elif isinstance(v, Convertible):
                return v.to_iterator()
            elif hasattr('unpack', v):
                return (x for x in v.unpack())
            else:
                return (x for x in [v, ])

        it = (v
              for vs in (f(v1) for v1 in self.to_iterator())
              for v in unpack(vs))
        return Iterator.from_iterator(it)

    def fold_left(self, b: B, f: FoldLeft[B, A]) -> B:
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (Callable[[B,A],B]): the function to fold with

        Returns:
            B: the result of folding
        """
        for a in self.get():
            b = f(b, a)
        return b

    def fold_right(self,
                   lb: Eval[B],
                   f: FoldRight[A, Eval[B]]
                   ) -> Eval[B]:
        """
        Performs right-associated fold using `f`. Uses lazy evaluation,
        requiring type `Eval[B]` for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (Callable[[A,Eval[B]],Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """

        def go(s):
            if s.is_empty():
                return lb
            else:
                head, tail = s.head_and_tail()
                return f(head, defer(lambda: tail.fold_right(lb, f)))

        return Now(self).flat_map(go)

    @staticmethod
    def from_iterator(it: typing.Iterator[A]) -> 'Iterator[A]':
        return Iterator(it)

    def get(self) -> typing.Iterator[A]:
        """
        Returns the iterator's inner value.

        Returns:
            Iterator[A]: the inner value
        """
        return self._value

    def head(self) -> A:
        """
        Returns the first item in the iterator.

        Returns:
            A: the first item

        Throws:
            StopIteration: if the iterator is empty
        """
        return next(self._value)

    def head_and_tail(self) -> Tuple[A, typing.Iterator[A]]:
        return next(self._value), self

    def head_option(self) -> Option[A]:
        """
        Safely returns the first item in the iterator by wrapping the attempt
        in `Option`.

        Returns:
            Option[T]: the first item wrapped in `Some`, or `Nothing` if the
                       list is empty
        """
        return mtry(lambda: self.head).to_option()

    # noinspection PyUnresolvedReferences,PyAttributeOutsideInit
    def is_empty(self) -> bool:
        test, self._value = itertools.tee(self._value)
        return mtry(lambda: next(test)).is_failure()

    # noinspection PyMethodMayBeStatic
    def is_gettable(self) -> bool:
        return True

    def last(self) -> A:
        """
        Returns the last item in the iterator.

        Returns:
            A: the last item

        Throws:
            StopIteration: if the iterator is empty
        """
        x = next(self._value)
        try:
            while True:
                x = next(self._value)
        except StopIteration:
            return x

    def last_option(self) -> Option[A]:
        """
        Safely returns the last item in the list by wrapping the attempt in
        `Option`.

        Returns:
            Option[A]: the first item wrapped in `Some`, or `Nothing` if the
                       list is empty
        """
        return mtry(lambda: self.last()).to_option()

    def map(self, f: F1[A, B]) -> 'Iterator[B]':
        """
        Applies a function to the inner value of a monad.

        Args:
            f (Callable[[A], B]): the function to apply

        Returns:
            Iterator[B]: the resulting Iterator
        """
        return Iterator.from_iterator((f(x) for x in self.get()))

    def memoize(self) -> 'Stream[A]':
        return self.to_stream()

    def mtail_option(self) -> Option['Iterator[A]']:
        """
        Returns the tail of the list as an option.

        Returns:
            Option[Iterator[A]]: the rest of the iterator
        """
        return mtry(lambda: self.tail()).to_option()

    @staticmethod
    def pure(*values: A) -> 'Iterator[A]':
        """
        Injects a value into the `Iterator` monad.

        Args:
            values (A): the values

        Returns:
            Iterator[A]: the resulting `Iterator`
        """
        return Iterator.from_iterator((x for x in values))

    def tail(self) -> 'Iterator[A]':
        """
        Returns the tail of the iterator.

        Returns:
            Iterator[A]: the tail of the list

        Throws:
            StopIteration: if the iterator is empty
        """
        next(self._value)
        return self

    def tail_option(self) -> Option['Iterator[A]']:
        """
        Returns the tail of the iterator as an option.

        Returns:
            Option[Iterator[A]]: the rest of the iterator
        """
        return mtry(lambda: self.tail()).to_option()

    # noinspection PyPep8Naming
    @staticmethod
    def tailrecM(f: F1[A, 'Iterator[Either[A, B]]'],
                 a: A
                 ) -> 'Iterator[B]':
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (Callable[[A], Iterator[Either[A, B]]]): the function to apply
            a (A): the recursive function's input

        Returns:
            Iterator[B]: an `F` instance containing the result of applying the
            tail-recursive function to its argument
        """

        def go(a1: A) -> 'Iterator[A]':
            fa = f(a1)
            e = fa.head()
            a2 = e.get()
            return fa.pure(a2) if e.is_right() else lambda: go(a2)

        return trampoline(go, a)

    def take(self, n: int) -> 'Iterator[A]':
        return Iterator(itertools.islice(self.get(), n))

    def take_while(self, p: Predicate[A]) -> 'Iterator[A]':
        return Iterator(itertools.dropwhile(p, self.get()))

    def to_iterator(self) -> 'Iterator[A]':
        return self

    def to_stream(self) -> 'Stream[A]':
        return Stream(self.get())

    def unpack(self) -> Tuple[A, ...]:
        """
        Returns the inner value as a tuple to support unpacking

        Returns:
            Tuple[A, ...]: the inner values as a tuple
        """
        return tuple(self.get())


def iterator(*values: A) -> 'Iterator[A]':
    """
    Constructs a `Iterator` instance from a tuple of values.

    Args:
        values (A): the values

    Returns:
        Iterator[A]: the resulting `Iterator`
    """
    return Iterator.pure(*values)


# noinspection PyMissingConstructor
class Stream(Iterator[A]):
    """
    A type that represents a memoized, lazy stream of values.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and
    `filter()` functions, and for-comprehensions can be formed by evaluating
    generators over monads with the `mfor()` function.
    """

    def __init__(self, it: typing.Iterator):
        self._value = it
        self._memo = None

    def __repr__(self) -> str:
        return 'Stream(%s)' % ', '.join(repr(x) for x in self.get())

    @staticmethod
    def from_iterator(it: typing.Iterator[A]) -> 'Stream[A]':
        return Stream(it)

    def get(self) -> typing.List[A]:
        """
        Returns the stream's inner value.

        Returns:
            typing.List[A]: the inner value
        """
        if self._memo is None:
            self._memo = [x for x in self._value]
        return self._memo

    @staticmethod
    def pure(*values: A) -> 'Stream[A]':
        """
        Injects a value into the `Stream` monad.

        Args:
            values (A): the values

        Returns:
            Stream[A]: the resulting `Stream`
        """
        return Stream((x for x in values))

    def to_iterator(self) -> Iterator[A]:
        return Iterator.from_iterator(self._value)

    def to_list(self) -> typing.List[A]:
        """
        Converts the `Stream` into a python list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return self.get()

    def to_stream(self) -> 'Stream[A]':
        return self


def stream(*values: A) -> Stream[A]:
    """
    Constructs a `Iterator` instance from a tuple of values.

    Args:
        values (A): the values

    Returns:
        Stream[A]: the resulting `Iterator`
    """
    return Stream.pure(*values)


def main():
    from genmonads.syntax import mfor
    import operator

    print(iterator(2, 3)
          .flat_map(lambda x: Iterator.pure(x + 5))
          .to_stream())

    # noinspection PyUnresolvedReferences
    print(mfor(x + y
               for x in iterator(2, 4, 6)
               if x < 5
               for y in iterator(5, 7, 9)
               if y % 3 != 0)
          .to_stream())

    def make_gen():
        for x in iterator(4):
            if x > 2:
                for y in iterator(10):
                    if y % 2 == 0:
                        yield x - y

    # noinspection PyUnresolvedReferences
    print(mfor(make_gen())
          .to_stream())

    # noinspection PyUnresolvedReferences
    print((iterator(5) >> (lambda x: iterator(x * 2)))
          .to_stream())

    print(iterator()
          .map(lambda x: x * 2)
          .to_stream())

    print(iterator(iterator(1, 2, 3, 4, 5), iterator(5, 4, 3, 2, 1))
          .flat_map(lambda x: x.last_option())
          .to_stream())

    n = 1000
    print(Iterator(itertools.count(1))
          .fold_right(Now(1),
                      lambda a, lb: lb.map(lambda b: a * b) if a < n else Now(a))
          .get())

    print(Iterator(itertools.count(1))
          .take(n)
          .fold_left(1, operator.mul))


if __name__ == '__main__':
    main()
