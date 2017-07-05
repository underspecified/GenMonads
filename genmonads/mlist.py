from genmonads.foldable import Foldable
from genmonads.monadfilter import MonadFilter
from genmonads.tailrec import trampoline

__all__ = ['List', 'Nil', 'mlist', 'nil']


class List(Foldable, MonadFilter):
    """
    A type that represents list of values of the same type.

    Instances are either of type `List[T]` or `Nil[T]`.

    Monadic computing is supported with `map()`, `flat_map()`, `flatten()`, and `filter()` functions,
    and for-comprehensions can be formed by evaluating generators over monads with the `mfor()` function.
    """

    def __init__(self, *values):
        self._value = list(values)

    def __eq__(self, other):
        """
        Args:
            other (List[T]): the value to compare against

        Returns:
            bool: `True` if other is an instance of `List` and inner values are equivalent, `False` otherwise
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
        return 'List'

    def __repr__(self):
        """
        Returns:
            str: a string representation of the List
        """
        return 'List(%s)' % ', '.join(repr(v) for v in self.get())

    @staticmethod
    def empty():
        """
        Returns:
            List[T]: `Nil`, the empty instance for this `MonadFilter`
        """
        return Nil()

    def flat_map(self, f):
        """
        Applies a function that produces an Monad from unwrapped values to an Monad's inner value and flattens the
        nested result.

        If the inner values can be converted to an instance of `List` by having an implementation of
        `to_mlist()`, the inner values will be converted to `List` before flattening. This allows for
        flattening of `List[Option[T]]` into `List[T]`, as is done in Scala.

        Args:
            f (Callable[[A],List[B]]): the function to apply

        Returns:
            List[B]: the resulting monad
        """
        def to_mlist(v):
            """
            Args:
                v (Union[F[T],T]): the value

            Returns:
                Iterator[T]: the empty instance for this `MonadFilter`
            """
            return (mtry(lambda: v.to_mlist().get())
                    .or_else(mtry(lambda: v.unpack()))
                    .get_or_else((v,)))

        from genmonads.mtry import mtry
        return List(*[v
                      for vs in (f(v1)for v1 in self.get())
                      for v in to_mlist(vs)])

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
        Performs left-associated fold using `f`. Uses lazy evaluation, requiring type `Eval[B]`
        for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (Callable[[A,Eval[B]],Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        for a in reversed(self.get()):
            lb = f(a, lb)
        return lb

    def get(self):
        """
        Returns the `List`'s inner value.

        Returns:
            list[T]: the inner value
        """
        return self._value

    def head(self):
        """
        Returns the first item in the list.

        Returns:
            T: the first item

        Throws:
            IndexError: if the list is empty
        """
        return self.get()[0]

    def head_option(self):
        """
        Safely returns the first item in the list by wrapping the attempt in `Option`.

        Returns:
            Option[T]: the first item wrapped in `Some`, or `Nothing` if the list is empty
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.head).to_option()

    # noinspection PyMethodMayBeStatic
    def is_gettable(self):
        return True

    def last(self):
        """
        Returns the last item in the list.

        Returns:
            T: the last item

        Throws:
            IndexError: if the list is empty
        """
        return self.get()[-1]

    def last_option(self):
        """
        Safely returns the last item in the list by wrapping the attempt in `Option`.

        Returns:
            Option[T]: the first item wrapped in `Some`, or `Nothing` if the list is empty
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.last()).to_option()

    def mtail(self):
        """
        Returns the tail of the list as a monadic List.

        Returns:
            List[T]: the rest of the nel
        """
        from genmonads.mtry import mtry
        return mtry(lambda: self.tail()).to_option().to_mlist()

    @staticmethod
    def pure(*values):
        """
        Injects a value into the `List` monad.

        Args:
            values (T): the values

        Returns:
            List[T]: the resulting `List`
        """
        return List(*values) if values else Nil()

    def tail(self):
        """
        Returns the tail of the list.

        Returns:
            typing.List[T]: the tail of the list
        """
        return self.get()[1:]

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

    def to_nel(self):
        """
        Tries to convert the `List` into a `NonEmptyList` monad.

        Returns:
            Option[NonEmptyList[A]]: the `NonEmptyList` wrapped in `Some` if the `List` is non-empty,
            `Nothing` otherwise
        """
        from genmonads.mtry import mtry
        from genmonads.nel import nel
        return mtry(lambda: nel(*self.get())).to_option()

    def unpack(self):
        return tuple(self.get())


def mlist(*values):
    """
    Constructs a `List` instance from a tuple of values.

    Args:
        values (T): the values

    Returns:
        stream.List[T]: the resulting `List`
    """
    return List.pure(*values)


# noinspection PyMissingConstructor,PyPep8Naming
class Nil(List):
    """
    A type that represents the empty list.
    """

    # noinspection PyInitNewSignature
    def __init__(self):
        self._value = []

    def __eq__(self, other):
        """
        Args:
            other (List[T]): the value to compare against

        Returns:
            bool: `True` if other is instance of `Nil`, `False` otherwise
        """
        if isinstance(other, Nil):
            return True
        else:
            return False

    def __repr__(self):
        """
        Returns:
            str: a string representation of the `List`
        """
        return 'Nil'


def nil():
    """
    Constructs a `Nil` instance.

    Returns:
        Nil[T]: the resulting `Nil`
    """
    return Nil()


def main():
    from genmonads.monad import mfor

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

    print(mlist(mlist(1, 2, 3, 4, 5), mlist(5, 4, 3, 2, 1)).flat_map(lambda x: x.last_option()))


if __name__ == '__main__':
    main()
