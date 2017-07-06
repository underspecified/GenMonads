from genmonads.functor import Functor
from genmonads.gettable import Gettable

__all__ = ['Applicative', ]


class Applicative(Functor, Gettable):
    """
    The applicative functor.
    """

    def __init__(self, *args, **kwargs):
        raise ValueError(
            """Tried to call the constructor of abstract base class Try.
            Use the try_to() or Try.pure() functions instead."""
        )

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the monad's name
        """
        return 'Applicative'

    def ap(self, ff):
        raise NotImplementedError

    def ap2(self, fb, ff):
        def go(a_b_f):
            a, (b, f) = a_b_f
            return f(a, b)
        return self.product(fb.product(ff)).map(go)

    def get(self):
        raise NotImplementedError

    def map(self, f):
        return self.ap(Applicative.pure(f))

    def map2(self, fb, f):
        def go(a_b):
            a, b = a_b
            return f(a, b)
        return self.product(fb).map(go)

    def map2_eval(self, fb, f):
        return fb.map(lambda _fb: self.map2(_fb, f))

    def product(self, fb):
        return fb.ap(self.map(lambda a: lambda b: (a, b)))

    @staticmethod
    def pure(value):
        raise NotImplementedError


def main():
    pass


if __name__ == '__main__':
    main()
