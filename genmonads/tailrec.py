from genmonads.either import *
from genmonads.flat_map import *
from genmonads.identity import *


def trampoline(f, *args, **kwargs):
    g = lambda: f(*args, **kwargs)
    while callable(g):
        g = g()
    return g

tailrec = trampoline


def main():
    def factorial(n, acc=1):
        if n == 0:
            return acc
        else:
            return lambda: factorial(n - 1, acc=n * acc)

    # noinspection PyPep8Naming
    def factorialM(args):
        n, acc = args
        ga = right(acc) if n == 0 else left((n - 1, n * acc))
        print("factorialM:", n, args, ga, identity(ga))
        return identity(ga)

    #print(trampoline(factorial, 1000))
    #print(FlatMap.tailrec(factorialM, (1000, 1)))


if __name__ == '__main__':
    main()
