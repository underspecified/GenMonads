import itertools

from genmonads.eval import Now, defer
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.tailrec import trampoline

__all__ = ['Iterator', 'iterator', 'Stream', 'stream']


class Iterator(Foldable, MonadFilter):
    """
    A type that represents a lazy iterator of values. Useful for representing python iterators and generators.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions,
    and for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, it):
        self._value = it

    def __eq__(self, other):
        """
        Args:
            other (Iterator[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Iterator` and inner values are equivalent, `False` otherwise
        """
        return type(self) == type(other) and self._value == other._value

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the monad's name
        """
        return 'Iterator'

    def __repr__(self):
        """
        Returns:
            str: a string representation of the Iterator
        """
        return 'Iterator(%s)' % str(self._value)

    def drop(self, n):
        return Iterator.from_iter(itertools.islice(self.get(), start=n))

    def drop_while(self, p):
        return Iterator.from_iter(itertools.dropwhile(self.get(), p))

    @staticmethod
    def empty():
        """
        Returns:
            Iterator[T]: the empty instance for this `MonadFilter`
        """
        return Iterator.from_iter((x for x in []))

    def filter(self, p):
        return Iterator.from_iter(filter(p, self.get()))

    def flat_map(self, f):
        """
        Applies a function that produces a iterator from unwrapped values to a iterator's inner value
        and flattens the nested result.

        Args:
            f (Callable[[A],Iterator[B]]): the function to apply

        Returns:
            Iterator[B]: the resulting iterator
        """

        def to_list(v):
            """
            Args:
                v (Union[F[T],T]): the value

            Returns:
                Iterator[T]: the empty instance for this `MonadFilter`
            """
            return (mtry(lambda: v.to_iter().to_list())
                    .or_else(mtry(lambda: [x for x in v.unpack()]))
                    .get_or_else([v, ]))

        from genmonads.mtry import mtry
        it = (v
              for vs in (f(v1) for v1 in self.to_list())
              for v in to_list(vs))
        return Iterator.from_iter(it)

    def fold_left(self, b, f):
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

    def fold_right(self, lb, f):
        """
        Performs right-associated fold using `f`. Uses lazy evaluation, requiring type `Eval[B]`
        for initial value and accumulation results.

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
    def from_iter(it):
        return Iterator(it)

    def get(self):
        """
        Returns the iterator's inner value.

        Returns:
            Iterator[T]: the inner value
        """
        return self._value

    def head(self):
        """
        Returns the first item in the iterator.

        Returns:
            T: the first item

        Throws:
            StopIteration: if the iterator is empty
        """
        return next(self._value)

    def head_and_tail(self):
        return next(self._value), self

    def head_option(self):
        """
        Safely returns the first item in the iterator by wrapping the attempt in `Option`.

        Returns:
            Option[T]: the first item wrapped in `Some`, or `Nothing` if the list is empty
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.head).to_option()

    # noinspection PyUnresolvedReferences,PyAttributeOutsideInit
    def is_empty(self):
        from genmonads.mtry import mtry
        test, self._value = itertools.tee(self._value)
        return mtry(lambda: next(test)).is_failure()

    # noinspection PyMethodMayBeStatic
    def is_gettable(self):
        return True

    def last(self):
        """
        Returns the last item in the iterator.

        Returns:
            T: the last item

        Throws:
            StopIteration: if the iterator is empty
        """
        x = next(self._value)
        try:
            while True:
                x = next(self._value)
        except StopIteration:
            return x

    def last_option(self):
        """
        Safely returns the last item in the list by wrapping the attempt in `Option`.

        Returns:
            Option[T]: the first item wrapped in `Some`, or `Nothing` if the list is empty
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.last()).to_option()

    def map(self, f):
        """
        Applies a function to the inner value of a monad.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Monad[B]: the resulting monad
        """
        return Iterator.from_iter((f(x) for x in self.get()))

    def memoize(self):
        return self.to_stream()

    def mtail_option(self):
        """
        Returns the tail of the list as an option.

        Returns:
            Option[Iterator[T]]: the rest of the iterator
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.tail()).to_option()

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `Iterator` monad.

        Args:
            values (T): the values

        Returns:
            Iterator[T]: the resulting `Iterator`
        """
        return Iterator.from_iter((x for x in values))

    def tail(self):
        """
        Returns the tail of the iterator.

        Returns:
            Iterator[T]: the tail of the list

        Throws:
            StopIteration: if the iterator is empty
        """
        next(self._value)
        return self

    def tail_option(self):
        """
        Returns the tail of the iterator as an option.

        Returns:
            Option[Iterator[T]]: the rest of the iterator
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.tail()).to_option()

    # noinspection PyPep8Naming
    @staticmethod
    def tailrecM(f, a):
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (Callable[[A],F[Either[A,B]]]): the function to apply
            a: the recursive function's input

        Returns:
            F[B]: an `F` instance containing the result of applying the tail-recursive function to
            its argument
        """

        def go(a1):
            fa = f(a1)
            e = fa.head()
            a2 = e.get()
            return fa.pure(a2) if e.is_right() else lambda: go(a2)

        return trampoline(go, a)

    def take(self, n):
        return Iterator(itertools.islice(self.get(), n))

    def take_while(self, p):
        return Iterator(itertools.dropwhile(self.get(), p))

    def to_iter(self):
        return self

    def to_stream(self):
        return Stream(self.get())

    def unpack(self):
        """
        Returns the inner value as a tuple to support unpacking

        Returns:
            Tuple[T]: the inner values as a tuple
        """
        return tuple(self.get())


def iterator(*values):
    """
    Constructs a `Iterator` instance from a tuple of values.

    Args:
        values (T): the values

    Returns:
        Iterator[T]: the resulting `Iterator`
    """
    return Iterator.pure(*values)


# noinspection PyMissingConstructor
class Stream(Iterator):
    """
    A type that represents a memoized, lazy stream of values.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions,
    and for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, it):
        self._value = it
        self._memo = None

    def __repr__(self):
        return 'Stream(%s)' % ', '.join(repr(x) for x in self.get())

    @staticmethod
    def from_iter(it):
        return Stream(it)

    def get(self):
        """
        Returns the iterator's inner value.

        Returns:
            Typing.List[T]: the inner value
        """
        if self._memo is None:
            self._memo = [x for x in self._value]
        return self._memo

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `Stream` monad.

        Args:
            values (T): the values

        Returns:
            Stream[T]: the resulting `Iterator`
        """
        return Stream((x for x in values))

    def to_iter(self):
        return Iterator.from_iter(self._value)

    def to_list(self):
        """
        Converts the `Stream` into a python list.

        Returns:
            typing.List[T]: the resulting python list
        """
        return self.get()

    def to_stream(self):
        return self


def stream(*values):
    """
    Constructs a `Iterator` instance from a tuple of values.

    Args:
        values (T): the values

    Returns:
        Stream[T]: the resulting `Iterator`
    """
    return Stream.pure(*values)


def main():
    from genmonads.monad import mfor
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
          .fold_right(Now(1), lambda a, lb: lb.map(lambda b: a * b) if a < n else Now(a))
          .get())

    print(Iterator(itertools.count(1))
          .take(n)
          .fold_left(1, operator.mul))


if __name__ == '__main__':
    main()
