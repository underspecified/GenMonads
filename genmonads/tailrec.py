__all__ = ['trampoline', ]


def trampoline(f, *args, **kwargs):
    g = lambda: f(*args, **kwargs)
    while callable(g):
        g = g()
    return g


def main():
    from genmonads.either import left, right
    from genmonads.nel import NonEmptyList

    def factorial(n, acc=1):
        if n == 0:
            return acc
        else:
            return lambda: factorial(n - 1, acc=n * acc)

    # noinspection PyPep8Naming
    def factorialM(args):
        n, acc = args[0:]
        ga = right(acc) if n == 0 else left((n - 1, n * acc))
        return NonEmptyList(ga)

    print(trampoline(factorial, 1000, 1))
    print(NonEmptyList.tailrecM(factorialM, (1000, 1)))


if __name__ == '__main__':
    main()
