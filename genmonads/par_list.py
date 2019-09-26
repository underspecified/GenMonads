import itertools
import typing
from multiprocessing import cpu_count

from multiprocess.pool import Pool

from genmonads.convertible import Convertible
from genmonads.either import Either
from genmonads.eval import Eval, Now, defer
from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.mtry_base import mtry
from genmonads.mytypes import *
from genmonads.option_base import Option
from genmonads.tailrec import trampoline

__all__ = ['ParList', 'Nil', 'par_list', 'nil', 'default_pool_settings']

default_pool_settings = {'processes': cpu_count(),
                         'chunksize': 1000}


EvalWithPool = F1[Pool, typing.Iterable[A]]


class ParList(MonadFilter[A],
              Foldable[A],
              Convertible[A]):
    """
    A type that represents list of values of the same type.

    Instances are either of type `List[A]` or `Nil`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and
    `filter()` functions, and for-comprehensions can be formed by evaluating
    generators over monads with the `mfor()` function.
    """

    def __init__(self, run: EvalWithPool[A]):
        self._run: EvalWithPool[A] = run

    def __eq__(self, other: 'ParList[A]') -> bool:
        """
        Args:
            other (ParList[A]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `List` and inner values are
             equivalent, `False` otherwise
        """
        return (type(self) == type(other)
                and self._run == other._run)

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the monad's name
        """
        return 'ParList'

    def __repr__(self) -> str:
        """
        Returns:
            str: a string representation of the List
        """
        return 'ParList(%s)' % self._run

    @staticmethod
    def empty() -> 'Nil':
        """
        Returns:
            ParList[A]: `Nil`, the empty instance for this `MonadFilter`
        """
        return Nil()

    def flat_map(self, f: F1[A, 'ParList[B]']) -> 'ParList[B]':
        """
        Applies a function that produces an Monad from unwrapped values to a
        Monad's inner value and flattens the nested result.

        If the inner values can be converted to an instance of `List` by having
        an implementation of to_par_list()`, the inner values will be converted to
        `List` before flattening. This allows for flattening of
        `List[Option[A]]` into `List[A]`, as is done in Scala.

        Args:
            f (F1[A, List[B]]): the function to apply

        Returns:
            ParList[B]: the resulting monad
        """
        # noinspection PyUnresolvedReferences
        def unpack(v: 'Union[A, Convertible[A]]',
                   pool: Pool
                   ) -> typing.Iterator[A]:
            """
            Args:
                v (Union[A, Convertible[A]): the value
                pool (Pool): the process pool

            Returns:
                Iterator[A]: the unpacked result
            """
            if isinstance(v, ParList):
                return v._run(pool)
            elif isinstance(v, Convertible):
                return v.to_iter()
            elif hasattr('unpack', v):
                return (x for x in v.unpack())
            else:
                return (x for x in [v, ])

        return ParList(lambda pool: (b
                                     for a in self._run(pool)
                                     for b in unpack(f(a), pool)))

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
        def go(s):
            if s.is_empty():
                return lb
            else:
                head, tail = next(s), s
                return f(head, defer(lambda: tail.fold_right(lb, f)))

        return Now(self.get()).flat_map(go)

    @staticmethod
    def from_iterator(it) -> 'ParList[A]':
        return ParList(lambda pool: it)

    def get(self) -> typing.Iterator[A]:
        """
        Returns the `List`'s inner value.

        Returns:
            typing.Iterator[A]: the inner value
        """
        return self.run()

    def head(self) -> A:
        """
        Returns the first item in the list.

        Returns:
            A: the first item

        Throws:
            StopIteration: if the iterator is empty
        """
        return next(self.get())

    def head_option(self) -> Option[A]:
        """
        Safely returns the first item in the list by wrapping the attempt in
        `Option`.

        Returns:
            Option[A]: the first item wrapped in `Some`, or `Nothing` if the
                       list is empty
        """
        return mtry(lambda: self.head).to_option()

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
        xs = self.get()
        x = next(xs)
        try:
            while True:
                x = next(xs)
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

    def map(self, f: F1[A, B]) -> 'ParList[B]':
        return ParList(lambda pool: pool.map(f,
                                             self._run(pool),
                                             chunksize=pool.chunksize))

    def mtail(self) -> 'ParList[A]':
        """
        Returns the tail of the list as a monadic List.

        Returns:
            ParList[A]: the rest of the list
        """
        return ParList(lambda pool: mtry(self._run(pool).tail()).to_iter())

    @staticmethod
    def pure(*values: A) -> 'ParList[A]':
        """
        Injects a value into the `List` monad.

        Args:
            values (A): the values

        Returns:
            ParList[A]: the resulting `List`
        """
        return ParList(lambda pool: list(values)) if values else Nil()

    def run(self, **pool_settings) -> typing.Iterator[A]:
        if not pool_settings:
            pool_settings = default_pool_settings
        chunksize = pool_settings.pop('chunksize')
        with Pool(**pool_settings) as pool:
            pool.__setattr__('chunksize', chunksize)
            values = self._run(pool)
        return values

    def tail(self) -> typing.Iterator[A]:
        """
        Returns the tail of the list.

        Returns:
            typing.Iterator[A]: the tail of the list

        Throws:
            StopIteration: if the iterator is empty

        """
        xs = self.get()
        next(xs)
        return xs

    # noinspection PyPep8Naming
    @staticmethod
    def tailrecM(f: F1[A, 'ParList[Either[A, B]]'], a: A) -> 'ParList[B]':
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (F1[A, 'List[Either[A, B]]']): the function to apply
            a (A): the recursive function's input

        Returns:
            F[B]: an `F` instance containing the result of applying the
                  tail-recursive function to its argument
        """

        def go(a1: A) -> Union[A, 'ParList[A]']:
            fa = f(a1)
            e = fa.head()
            a2 = e.get()
            return fa.pure(a2) if e.is_right() else lambda: go(a2)

        return trampoline(go, a)

    def to_iter(self) -> typing.Iterator[A]:
        """
        Converts the `List` into a python iterator.

        Returns:
            typing.Iterator[A]: the resulting python iterator
        """
        return self.get()

    def unpack(self) -> Tuple[A, ...]:
        """
        Returns the inner value as a tuple to support unpacking

        Returns:
            Tuple[A]: the inner values as a tuple
        """
        return tuple(self.get())


def par_list(*values: A) -> 'ParList[A]':
    """
    Constructs a `List` instance from a tuple of values.

    Args:
        values (A): the values

    Returns:
        stream.List[A]: the resulting `List`
    """
    return ParList.pure(*values)


# noinspection PyMissingConstructor,PyPep8Naming
class Nil(ParList):
    """
    A type that represents the empty list.
    """

    # noinspection PyInitNewSignature
    def __init__(self):
        self.run = lambda pool: []

    def __eq__(self, other: 'ParList[A]'):
        """
        Args:
            other (ParList[A]): the value to compare against

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

    def get(self):
        return []

    def flat_map(self, f: F1[A, ParList[B]]) -> 'Nil':
        return self

    def map(self, f: F1[A, B]) -> 'Nil':
        return self


def nil() -> Nil:
    """
    Constructs a `Nil` instance.

    Returns:
        Nil: the resulting `Nil`
    """
    return Nil()


def main():
    from genmonads.syntax import mfor

    # print(par_list(1, 2, 3, 4, 5)
    #       .get())
    #
    # print(par_list(1, 2, 3, 4, 5)
    #       .map(lambda x: x + 1)
    #       .get())
    #
    # print(par_list(1, 2, 3, 4, 5)
    #       .flat_map(lambda x: par_list(x * 2))
    #       .flat_map(lambda x: par_list(x - 1))
    #       .get())
    #
    # def f(x, factory=ParList.pure):
    #     return factory(x + 5)
    #
    # print(par_list(2, 3)
    #       .flat_map(lambda x: f(x))
    #       .get())
    #
    # print(par_list(2, 3)
    #       .flat_map(lambda x: par_list(x + 5))
    #       .get())
    #
    # print(par_list(2, 4, 6)
    #       .filter(lambda x: x < 10)
    #       .flat_map(lambda x: par_list(5, 7, 9)
    #                 .filter(lambda y: y % 2 != 0)
    #                 .map(lambda y: x + y))
    #       .get())
    #
    # print(mfor(x + y
    #            for x in par_list(2, 4, 6)
    #            if x < 10
    #            for y in par_list(5, 7, 9)
    #            if y % 2 != 0)
    #       .get())
    #
    # def make_gen():
    #     for x in par_list(4):
    #         if x > 2:
    #             for y in par_list(10):
    #                 if y % 2 == 0:
    #                     yield x - y
    #
    # print(mfor(make_gen())
    #       .get())
    #
    # print((par_list(5) >> (lambda x: par_list(x * 2)))
    #       .get())
    #
    # print(nil()
    #       .map(lambda x: x * 2)
    #       .get())
    #
    # print(par_list(par_list(1, 2, 3, 4, 5), par_list(5, 4, 3, 2, 1))
    #       .flat_map(lambda x: x.last_option())
    #       .get())

    import fileinput
    lines = itertools.islice(fileinput.input(), 1000000)
    out: ParList[str] = mfor(x[::-1].upper()
                             for x in ParList.from_iterator(lines))
    for line in out.run(chunksize=1000):
        print(line)


if __name__ == '__main__':
    main()
