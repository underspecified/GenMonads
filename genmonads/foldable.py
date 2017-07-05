from genmonads.eval import Later, Now
# noinspection PyProtectedMember
from genmonads.match import _

__all__ = ['Foldable', ]


class Foldable:
    """
    A type that represents foldable data structures.
    """

    # noinspection PyProtectedMember
    def _reduce_left_to_option(self, f, g):
        """
        Args:
            f (Callable[[A],B]): the function used to produce a `B` from the final `A` value 
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
    def _reduce_right_to_option(self, f, g):
        """
        Args:
            f (Callable[[A],B]): the function used to produce a `B` from the final `A` value 
            g (Callable[[A],Eval[B]],Eval[B]]): the function to reduce with

        Returns:
            Option[B]: the result of reduction
        """
        from genmonads.option import Nothing, Some
        return self.fold_right(
            Now(Nothing()),
            lambda fb, a: fb.match({
                Some(_):
                    lambda b: g(a, Now(b)).map(lambda bb: Some(bb)),
                Nothing():
                    lambda: Later(lambda: Some(f(a)))
            }))

    def contains(self, elem):
        """
        Checks if any of this monad's inner values is equivalent to `elem`.

        Args:
            elem (A): the element

        Returns:
            bool: True if any of this monad's inner values is equivalent to `elem`
        """
        return self.exists(lambda x: elem == x)

    def drop_while_(self, p):
        """
        Args:
            p (Callable[[A],bool]): the predicate

        Returns:
            stream.List[A]: a list of consecutive elements at the beginning of the `Foldable` that `p` does not match
        """
        return self.fold_right(
            Now([]),
            lambda a, llst: Now([]) if p(a) else llst.map(lambda lst: [a, ] + lst)
        ).get()

    def exists(self, p):
        """
        Checks if the predicate is `True` for any of this `Foldable`'s inner values .

        Args:
            p (Callable[[A],bool]): the predicate

        Returns:
            bool: True if the predicate is `True` for any of this monad's inner values
        """
        return self.find(p).is_defined()

    def filter_(self, p):
        """
        Args:
            p (Callable[[A],bool]): the predicate

        Returns:
            List[A]: a list of the elements that `p` matches
        """
        return self.fold_left(
            [],
            lambda lst, a: lst + [a, ] if p(a) else lst)

    def find(self, p):
        """
        Finds the first element that matches the predicate, if one exists.

        Args:
            p (Callable[[A]],bool]): the predicate

        Returns:
            Option[A]: the first element matching the predicate, if one exists
        """
        from genmonads.option import Nothing, Some
        return self.fold_right(
            Now(Nothing()),
            lambda a, lb: Now(Some(a)) if p(a) else lb
        ).get()

    def fold_left(self, b, f):
        """
        Performs left-associated fold using `f`. Uses eager evaluation.

        Args:
            b (B): the initial value
            f (Callable[[B,A],B]): the function to fold with

        Returns:
            B: the result of folding
        """
        raise NotImplementedError

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
        raise NotImplementedError

    def forall(self, p):
        """
        Checks if the predicate is `True` for all of this monad's inner values or the monad is empty.

        Args:
            p (Callable[[A],bool]): the predicate

        Returns:
            bool: True if the predicate is True for all of this monad's inner values or the monad is empty,
            False otherwise
        """
        return self.fold_right(
            Now(True),
            lambda a, lb: lb if p(a) else Now(False)
        ).get()

    def is_empty(self):
        """
        Returns:
            bool: `True` if there are no elements, `False` otherwise
        """
        return self.fold_right(
            Now(True),
            lambda a, lb: Now(False)
        ).get()

    def non_empty(self):
        """
        Returns:
            bool: `True` if there are any elements, `False` otherwise
        """
        return not self.is_empty()

    def reduce_left_option(self, f):
        """
        Args:
            f (Callable[[A,A],A]): the function to reduce with

        Returns:
            Option[A]: the result of reduction
        """
        return self._reduce_left_to_option(lambda x: x, f)

    def reduce_right_option(self, f):
        """
        Args:
            f (Callable[[A,Eval[A]],A]): the function to reduce with

        Returns:
            Eval[Option[A]]: the result of reduction
        """
        return self._reduce_right_to_option(lambda x: x, f)

    def to_iter(self):
        """
        Converts the `Foldable` into an iterator.

        Returns:
            Iterator[A]: the resulting python list
        """
        from genmonads.iterator import Iterator
        return Iterator(self.to_list())

    def to_list(self):
        return self.fold_left(
            [],
            lambda lst, a: lst + [a, ]
        )

    def to_mlist(self):
        from genmonads.mlist import List
        return List(*self.to_list())

    def to_stream(self):
        """
        Converts the `Foldable` into a stream.

        Returns:
            Stream[A]: the resulting python list
        """
        from genmonads.iterator import Stream
        return Stream(self.to_list())

    def take_while_(self, p):
        """
        Args:
            p (Callable[[A],bool]): the predicate

        Returns:
            List[T]: a list of consecutive elements at the beginning of the `Foldable` that `p` matches
        """
        self.fold_right(
            Now([]),
            lambda a, llst: llst.map(lambda lst: [a, ] + lst) if p(a) else Now([])
        ).get()
