from genmonads.functor import *


__all__ = ['FlatMap', ]


class FlatMap(Functor):
    """
    A type class for that implements the `flat_map()` function.
    """

    def __lshift__(self, fb):
        """
        A symbolic alias for `for_effect()`.

        Args:
            fb (FlatMap[B]]): the `FlatMap` to evaluate and discard output

        Returns:
            FlatMap[A]
        """
        return self.for_effect(fb)

    def __rshift__(self, f):
        """
        A symbolic alias for `flat_map()` and `followed_by()`.
        
        Uses dynamic type checking to permit arguments of the forms `self >> lambda x: FlatMap(x)` and
        `self >> FlatMap(x)`, where the latter discards the output of the first `FlatMap` instance.

        Args:
            f (Union[Callable[[A],FlatMap[B]],FlatMap[B]]): the function to apply

        Returns:
            FlatMap[B]
        """
        return self.flat_map(f) if callable(f) else self.followed_by(f)

    def flatten(self):
        """
        Flattens nested `F` structures.

        Returns:
            FlatMap[T]: the flattened monad
        """
        return self.flat_map(lambda fa: fa)

    def flat_map(self, f):
        """
        Applies a function to the inner value of a monad.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            FlatMap[B]: the resulting monad
        """
        raise NotImplementedError

    def followed_by(self, fb):
        """
        Sequentially compose two `FlatMap`s, discarding the output of the first.

        Args:
            fb (FlatMap[B]): the `FlatMap` to return

        Returns:
            FlatMap[B]: the resulting `FlatMap` after evaluating the first and discarding its output
        """
        return self.flat_map(lambda _: fb)

    def for_effect(self, fb):
        """
        Sequentially compose two `FlatMap`s, discarding the output of the first.

        Args:
            fb (FlatMap[B]): the `FlatMap` to return

        Returns:
            FlatMap[B]: the resulting `FlatMap` after evaluating the first and discarding its output
        """
        return self.flat_map(lambda a: fb.map(lambda _: a))

    def map(self, f):
        """
        Applies a function to the inner value of a functor.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            FlatMap[B]: the resulting functor
        """
        raise NotImplementedError

    @staticmethod
    def pure(value):
        """
        Injects a value into `FlatMap`.

        Args:
            value (T): the value

        Returns:
            FlatMap[T]: the resulting `FlatMap`
        """
        raise NotImplementedError

    @staticmethod
    def tailrec(f, a):
        """
        Applies a tail-recursive function in a stack safe manner.

        Args:
            f (Callable[[A],F[Either[A,B]]]): the function to apply
            a: the recursive function's input

        Returns:
            FlatMap[B]: a `FlatMap` instance containing the result of applying the tail-recursive function to 
            its argument
        """
        fa = f(a)

        def go(ga):
            print("tailrec.go(%s) ..." % ga)
            ab = ga.get()
            return f(ab).flat_map(go) if ga.is_left() else fa.pure(ab)

        return fa.flat_map(go)
