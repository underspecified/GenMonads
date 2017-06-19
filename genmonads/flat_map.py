from genmonads.functor import *

__all__ = ['FlatMap', ]


def trampoline(f, *args, **kwargs):
    g = lambda: f(*args, **kwargs)
    while callable(g):
        g = g()
    return g


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
            e = fa.get()
            a2 = e.get()
            if e.is_left():
                return lambda: go(a2)
            else:
                return fa.pure(a2)
        return trampoline(go, a)

