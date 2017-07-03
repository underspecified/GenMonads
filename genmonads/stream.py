import itertools

from genmonads.eval import Now, defer
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.tailrec import trampoline

__all__ = ['Stream', 'stream']


class Stream(Foldable, MonadFilter):
    """
    A type that represents a memoized stream of values.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions,
    and for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, gen):
        self._value = gen

    def __eq__(self, other):
        """
        Args:
            other (Stream[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `Stream` and inner values are equivalent, `False` otherwise
        """
        return type(self) == type(other) and self._value == other._value

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the monad's name
        """
        return 'Stream'

    def __repr__(self):
        """
        Returns:
            str: a string representation of the Stream
        """
        return 'Stream(%s)' % str(self._value)

    @staticmethod
    def empty():
        """
        Returns:
            Stream[T]: the empty instance for this `MonadFilter`
        """
        return Stream((x for x in []))

    # noinspection PyProtectedMember
    def flat_map(self, f):
        """
        Applies a function that produces a stream from unwrapped values to a stream's inner value
        and flattens the nested result.

        Args:
            f (Callable[[A],Stream[B]]): the function to apply

        Returns:
            Stream[B]: the resulting stream
        """
        return Stream.from_gen((v
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
        for a in self._value:
            b = f(a, b)
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
    def from_gen(gen):
        return Stream(gen)

    def get(self):
        """
        Returns the stream's inner value.

        Returns:
            List[T]: the inner value
        """
        value, self._value = itertools.tee(self._value)
        return [x for x in value]

    def head(self):
        """
        Returns the first item in the stream.

        Returns:
            T: the first item

        Throws:
            StopIteration: if the stream is empty
        """
        return next(self._value)

    def head_and_tail(self):
        return next(self._value), Stream(self._value)

    def head_option(self):
        """
        Safely returns the first item in the stream by wrapping the attempt in `Option`.

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
        Returns the last item in the stream.

        Returns:
            T: the last item

        Throws:
            StopIteration: if the stream is empty
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
        return Stream.from_gen((f(x) for x in self._value))

    def mtail_option(self):
        """
        Returns the tail of the list as an option.

        Returns:
            Option[Stream[T]]: the rest of the stream
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.tail()).to_option()

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `Stream` monad.

        Args:
            values (T): the values

        Returns:
            Stream[T]: the resulting `Stream`
        """
        return Stream((x for x in values))

    def tail(self):
        """
        Returns the tail of the stream.

        Returns:
            Stream[T]: the tail of the list

        Throws:
            StopIteration: if the stream is empty
        """
        next(self._value)
        return Stream.from_gen(self._value)

    def tail_option(self):
        """
        Returns the tail of the stream as an option.

        Returns:
            Option[Stream[T]]: the rest of the stream
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


def stream(*values):
    """
    Constructs a `Stream` instance from a tuple of values.

    Args:
        values (T): the values

    Returns:
        stream.Stream[T]: the resulting `Stream`
    """
    return Stream.pure(*values)


def main():
    from genmonads.monad import mfor
    import itertools

    print(stream(2, 3)
          .flat_map(lambda x: Stream.pure(x + 5))
          .get())

    print(mfor(x + y
               for x in stream(2, 4, 6)
               if x < 10
               for y in stream(5, 7, 9)
               if y % 2 != 0)
          .get())

    def make_gen():
        for x in stream(4):
            if x > 2:
                for y in stream(10):
                    if y % 2 == 0:
                        yield x - y

    print(mfor(make_gen())
          .get())

    print((stream(5) >> (lambda x: stream(x * 2)))
          .get())

    print(stream()
          .map(lambda x: x * 2)
          .get())

    print(stream(stream(1, 2, 3, 4, 5), stream(5, 4, 3, 2, 1))
          .flat_map(lambda x: x.last_option()
                               .map(lambda y: stream(y))
                               .get_or_else(Stream.empty()))
          .get())

    print(Stream
          .from_gen(itertools.count())
          .fold_right(Now(0), lambda a, lb: lb if a < 5 else Now(a))
          .get())


if __name__ == '__main__':
    main()
