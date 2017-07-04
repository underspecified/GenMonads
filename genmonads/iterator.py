import itertools

from genmonads.eval import Now, defer
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.tailrec import trampoline

__all__ = ['Iterator', 'iterator']


class Iterator(Foldable, MonadFilter):
    """
    A type that represents an iterator of values.

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

    @staticmethod
    def empty():
        """
        Returns:
            Iterator[T]: the empty instance for this `MonadFilter`
        """
        return Iterator((x for x in []))

    def filter(self, p):
        return Iterator.from_iter(*filter(p, self._value))

    # noinspection PyProtectedMember
    def flat_map(self, f):
        """
        Applies a function that produces a iterator from unwrapped values to a iterator's inner value
        and flattens the nested result.

        Args:
            f (Callable[[A],Iterator[B]]): the function to apply

        Returns:
            Iterator[B]: the resulting iterator
        """
        return Iterator.from_iter((v
                                  for vs in (f(v1) for v1 in self._value)
                                  for v in vs._value))

    def fold_left(self, b, f):
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (Callable[[B,A],B]): the function to fold with

        Returns:
            B: the result of folding
        """
        return b if self.is_empty() else itertools.accumulate(self._value, f)

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
            List[T]: the inner value
        """
        value, self._value = itertools.tee(self._value)
        return [x for x in value]

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
        return next(self._value), Iterator(self._value)

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
        return Iterator.from_iter((f(x) for x in self._value))

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
        return Iterator((x for x in values))

    def tail(self):
        """
        Returns the tail of the iterator.

        Returns:
            Iterator[T]: the tail of the list

        Throws:
            StopIteration: if the iterator is empty
        """
        next(self._value)
        return Iterator.from_iter(self._value)

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

    def unpack(self):
        return tuple(self.get())


def iterator(*values):
    """
    Constructs a `Iterator` instance from a tuple of values.

    Args:
        values (T): the values

    Returns:
        iterator.Iterator[T]: the resulting `Iterator`
    """
    return Iterator.pure(*values)


def main():
    from genmonads.monad import mfor
    import itertools

    print(iterator(2, 3)
          .flat_map(lambda x: Iterator.pure(x + 5))
          .get())

    print(mfor(x + y
               for x in iterator(2, 4, 6)
               if x < 10
               for y in iterator(5, 7, 9)
               if y % 2 != 0)
          .get())

    def make_gen():
        for x in iterator(4):
            if x > 2:
                for y in iterator(10):
                    if y % 2 == 0:
                        yield x - y

    print(mfor(make_gen())
          .get())

    print((iterator(5) >> (lambda x: iterator(x * 2)))
          .get())

    print(iterator()
          .map(lambda x: x * 2)
          .get())

    print(iterator(iterator(1, 2, 3, 4, 5), iterator(5, 4, 3, 2, 1))
          .flat_map(lambda x: x.last_option()
                               .map(lambda y: iterator(y))
                               .get_or_else(Iterator.empty()))
          .get())

    print(Iterator
          .from_iter(itertools.count())
          .fold_right(Now(0), lambda a, lb: lb if a < 5 else Now(a))
          .get())


if __name__ == '__main__':
    main()
