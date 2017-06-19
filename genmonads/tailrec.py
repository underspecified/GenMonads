from genmonads.either import *
from genmonads.mtry import *

__all__ = ['trampoline', ]


def trampoline(f, *args, **kwargs):
    g = lambda: f(*args, **kwargs)
    while callable(g):
        g = g()
    return g


def main():
    def factorial(n, acc=1):
        if n == 0:
            return acc
        else:
            return lambda: factorial(n - 1, acc=n * acc)

    # noinspection PyPep8Naming
    def factorialM(args):
        n, acc = args[0:]
        ga = right(acc) if n == 0 else left((n - 1, n * acc))
        return Success(ga)

    print(trampoline(factorial, 1000, 1))
    print(Try.tailrecM(factorialM, (1000, 1)))


if __name__ == '__main__':
    main()
