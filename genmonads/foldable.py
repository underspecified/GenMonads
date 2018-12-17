from genmonads.match import _
from genmonads.mytypes import *

__all__ = ['Foldable', ]


# noinspection PyUnresolvedReferences
class Foldable(Generic[A]):
    """
    A type that represents foldable data structures.
    """

    def __contains__(self, elem: A) -> bool:
        """
        Checks if any of this monad's inner values is equivalent to `elem`.

        Args:
            elem (A): the element

        Returns:
            bool: True if any of this monad's inner values is equivalent to
                  `elem`
        """
        return self.exists(lambda x: elem == x)

    # noinspection PyProtectedMember
    def _reduce_left_to_option(self,
                               f: Callable[[A], B],
                               g: Callable[[B, A], B]
                               ) -> 'Option[B]':
        """
        Args:
            f (Callable[[A],B]): the function used to produce a `B` from the
                                 final `A` value
            g (Callable[[B,A],B]): the function to reduce with

        Returns:
            Option[B]: the result of reduction
        """
        from genmonads.option import Nothing, Some
        return self.fold_left(
            Nothing(),
            lambda fb, a: fb.match({
                Some(_):
                    lambda b: Some(g(b, a)),
                Nothing():
                    lambda: Some(f(a))
            }))

    # noinspection PyProtectedMember
    def _reduce_right_to_option(self,
                                f: Callable[[A], B],
                                g: Callable[[A, 'Eval[B]'], 'Eval[B]']
                                ) -> 'Eval[Option[B]]':
        """
        Args:
            f (Callable[[A], B]): the function used to produce a `B` from the
                                 final `A` value
            g (Callable[[A, Eval[B]], Eval[B]]): the function to reduce with

        Returns:
            Eval[Option[B]]: the result of reduction
        """
        from genmonads.eval import Later, Now
        from genmonads.option import Option, Nothing, Some
        return self.fold_right(
            Now(Nothing()),
            lambda fb, a: fb.match({
                Some(_):
                    lambda b: g(a, Now(b)).map(lambda bb: Some(bb)),
                Nothing():
                    lambda: Later(lambda: Some(f(a)))
            }))

    def contains(self, elem: A) -> bool:
        """
        Checks if any of this monad's inner values is equivalent to `elem`.

        Args:
            elem (A): the element

        Returns:
            bool: True if any of this monad's inner values is equivalent to
                  `elem`
        """
        return self.__contains__(elem)

    def drop_while_(self, p: Callable[[A], bool]) -> List[A]:
        """
        Args:
            p (Callable[[A], bool]): the predicate

        Returns:
            typing.List[A]: a list of consecutive elements at the beginning of
                            the `Foldable` that `p` does not match
        """
        from genmonads.eval import Now
        return self.fold_right(
            Now([]),
            lambda a, llst: Now([]) if p(a) else llst.map(lambda lst: [a, ] + lst)
        ).get()

    def exists(self, p: Callable[[A], bool]) -> bool:
        """
        Checks if the predicate is `True` for any of this `Foldable`'s inner
        values .

        Args:
            p (Callable[[A], bool]): the predicate

        Returns:
            bool: True if the predicate is `True` for any of this monad's inner
                  values
        """
        return self.find(p).is_defined()

    def filter_(self, p: Callable[[A], bool]) -> List[A]:
        """
        Args:
            p (Callable[[A], bool]): the predicate

        Returns:
            typing.List[A]: a list of the elements that `p` matches
        """
        return self.fold_left(
            [],
            lambda lst, a: lst + [a, ] if p(a) else lst)

    def find(self, p: Callable[[A], bool]) -> 'Option[A]':
        """
        Finds the first element that matches the predicate, if one exists.

        Args:
            p (Callable[[A], bool]): the predicate

        Returns:
            Option[A]: the first element matching the predicate, if one exists
        """
        from genmonads.eval import Now
        from genmonads.option import Option, Nothing, Some
        return self.fold_right(
            Now(Nothing()),
            lambda a, lb: Now(Some(a)) if p(a) else lb
        ).get()

    def fold_left(self, b: B, f: Callable[[B, A], B]) -> B:
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (Callable[[B,A],B]): the function to fold with

        Returns:
            B: the result of folding
        """
        raise NotImplementedError

    def fold_right(self,
                   lb: 'Eval[B]',
                   f: Callable[[A, 'Eval[B]'], 'Eval[B]']
                   ) -> 'Eval[B]':
        """
        Performs right-associated fold using `f`. Uses lazy evaluation,
        requiring type `Eval[B]` for initial value and accumulation results.

        Args:
            lb (Eval[B]): the lazily-evaluated initial value
            f (Callable[[A,Eval[B]],Eval[B]]): the function to fold with

        Returns:
            Eval[B]: the result of folding
        """
        raise NotImplementedError

    def forall(self, p: Callable[[A], bool]) -> bool:
        """
        Checks if the predicate is `True` for all of this monad's inner values
        or the monad is empty.

        Args:
            p (Callable[[A],bool]): the predicate

        Returns:
            bool: True if the predicate is True for all of this monad's inner
                  values or the monad is empty, False otherwise
        """
        from genmonads.eval import Now
        return self.fold_right(
            Now(True),
            lambda a, lb: lb if p(a) else Now(False)
        ).get()

    def is_empty(self) -> bool:
        """
        Returns:
            bool: `True` if there are no elements, `False` otherwise
        """
        from genmonads.eval import Now
        return self.fold_right(
            Now(True),
            lambda a, lb: Now(False)
        ).get()

    def non_empty(self) -> bool:
        """
        Returns:
            bool: `True` if there are any elements, `False` otherwise
        """
        return not self.is_empty()

    def reduce_left_option(self, f: Callable[[A, A], A]) -> 'Option[A]':
        """
        Args:
            f (Callable[[A,A],A]): the function to reduce with

        Returns:
            Option[A]: the result of reduction
        """
        return self._reduce_left_to_option(lambda x: x, f)

    def reduce_right_option(self,
                            f: Callable[[A, 'Eval[A]'], A]
                            ) -> 'Eval[Option[A]]':
        """
        Args:
            f (Callable[[A,Eval[A]],A]): the function to reduce with

        Returns:
            Eval[Option[A]]: the result of reduction
        """
        return self._reduce_right_to_option(lambda x: x, f)

    def to_iter(self) -> 'MIterator[A]':
        """
        Converts the `Foldable` into an iterator.

        Returns:
            genmonads.iterator.Iterator[A]: the resulting python iterator
        """
        from genmonads.iterator import Iterator as MIterator
        return MIterator.pure(*self.to_list())

    def to_list(self) -> List[A]:
        """
        Converts the `Foldable` into a stream.

        Returns:
            typing.List[A]: the resulting python list
        """
        return self.fold_left(
            [],
            lambda lst, a: lst + [a, ]
        )

    def to_mlist(self) -> 'MList[A]':
        """
        Converts the `Foldable` into a monadic list.

        Returns:
            genmonads.mlist.List[A]: the resulting python list
        """
        from genmonads.mlist import List as MList
        return MList(*self.to_list())

    def to_nel(self) -> 'Option[NonEmptyList[A]]':
        """
        Tries to convert the `Foldable` into a `NonEmptyList` monad.

        Returns:
            Option[NonEmptyList[A]]: the `NonEmptyList` wrapped in `Some` if
                                     the `List` is non-empty, `Nothing`
                                     otherwise
        """
        from genmonads.mtry import mtry
        from genmonads.nel import nel
        return mtry(lambda: nel(*self.to_list())).to_option()

    def to_stream(self) -> 'Stream[A]':
        """
        Converts the `Foldable` into a stream.

        Returns:
            Stream[A]: the resulting Stream
        """
        from genmonads.iterator import Stream
        return Stream.pure(*self.to_list())

    def take_while_(self, p: Callable[[A], bool]) -> List[A]:
        """
        Args:
            p (Callable[[A], bool]): the predicate

        Returns:
            typing.List[A]: a list of consecutive elements at the beginning of
                            the `Foldable` that `p` matches
        """
        from genmonads.eval import Now
        return self.fold_right(
            Now([]),
            lambda a, llst: llst.map(lambda lst: [a, ] + lst) if p(a) else Now([])
        ).get()
