import typing

from genmonads.eval import Eval, Later, Now
from genmonads.match import _
from genmonads.mytypes import *
from genmonads.option_base import Option, Nothing, Some

__all__ = ['Foldable', ]


class Foldable(Container[A]):
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
                               f: F1[A, B],
                               g: FoldLeft[B, A],
                               ) -> 'Option[B]':
        """
        Args:
            f (F1[A, B]): the function used to produce a `B` from the
                                 final `A` value
            g (FoldLeft[B, A]): the function to reduce with

        Returns:
            Option[B]: the result of reduction
        """
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
                                f: F1[A, B],
                                g: FoldRight[A, 'Eval[B]']
                                ) -> 'Eval[Option[B]]':
        """
        Args:
            f (Callable[[A], B]): the function used to produce a `B` from the
                                 final `A` value
            g (Callable[[A, Eval[B]], Eval[B]]): the function to reduce with

        Returns:
            Eval[Option[B]]: the result of reduction
        """
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

    def drop_while_(self, p: Predicate[A]) -> typing.List[A]:
        """
        Args:
            p (Predicate[A]): the predicate

        Returns:
            typing.List[A]: a list of consecutive elements at the beginning of
                            the `Foldable` that `p` does not match
        """
        return self.fold_right(
            Now([]),
            lambda a, llst: Now([]) if p(a) else llst.map(lambda lst: [a, ] + lst)
        ).get()

    def exists(self, p: Predicate[A]) -> bool:
        """
        Checks if the predicate is `True` for any of this `Foldable`'s inner
        values .

        Args:
            p (Predicate[A]): the predicate

        Returns:
            bool: True if the predicate is `True` for any of this monad's inner
                  values
        """
        return self.find(p).is_defined()

    def filter_(self, p: Predicate[A]) -> typing.List[A]:
        """
        Args:
            p (Predicate[A]): the predicate

        Returns:
            typing.List[A]: a list of the elements that `p` matches
        """
        return self.fold_left(
            [],
            lambda lst, a: lst + [a, ] if p(a) else lst)

    def find(self, p: Predicate[A]) -> 'Option[A]':
        """
        Finds the first element that matches the predicate, if one exists.

        Args:
            p (Predicate[A]): the predicate

        Returns:
            Option[A]: the first element matching the predicate, if one exists
        """
        return self.fold_right(
            Now(Nothing()),
            lambda a, lb: Now(Some(a)) if p(a) else lb
        ).get()

    def fold_left(self, b: B, f: FoldLeft[B, A]) -> B:
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
                   f: FoldRight[A, 'Eval[B]']
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

    def forall(self, p: Predicate[A]) -> bool:
        """
        Checks if the predicate is `True` for all of this monad's inner values
        or the monad is empty.

        Args:
            p (Predicate[A]): the predicate

        Returns:
            bool: True if the predicate is True for all of this monad's inner
                  values or the monad is empty, False otherwise
        """
        return self.fold_right(
            Now(True),
            lambda a, lb: lb if p(a) else Now(False)
        ).get()

    def is_empty(self) -> bool:
        """
        Returns:
            bool: `True` if there are no elements, `False` otherwise
        """
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

    def reduce_left_option(self, f: FoldLeft[A, A]) -> 'Option[A]':
        """
        Args:
            f (Callable[[A,A],A]): the function to reduce with

        Returns:
            Option[A]: the result of reduction
        """
        return self._reduce_left_to_option(lambda x: x, f)

    def reduce_right_option(self,
                            f: FoldRight[A, 'Eval[A]']
                            ) -> 'Eval[Option[A]]':
        """
        Args:
            f (Callable[[A,Eval[A]],A]): the function to reduce with

        Returns:
            Eval[Option[A]]: the result of reduction
        """
        return self._reduce_right_to_option(lambda x: x, f)

    def to_list(self) -> typing.List[A]:
        """
        Converts the `Foldable` into a python list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return self.fold_left(
            [],
            lambda lst, a: lst + [a, ]
        )

    def take_while_(self, p: Predicate[A]) -> typing.List[A]:
        """
        Args:
            p (Predicate[A]): the predicate

        Returns:
            typing.List[A]: a list of consecutive elements at the beginning of
                            the `Foldable` that `p` matches
        """
        return self.fold_right(
            Now([]),
            lambda a, llst: llst.map(lambda lst: [a, ] + lst) if p(a) else Now([])
        ).get()
