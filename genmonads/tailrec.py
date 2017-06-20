__all__ = ['trampoline', ]


def trampoline(f, *args, **kwargs):
    g = lambda: f(*args, **kwargs)
    while callable(g):
        g = g()
    return g


# noinspection PyPep8Naming
def main():
    from genmonads.either import left, right
    from genmonads.mtry import Failure, Success, Try

    def factorial(args):
        n, acc = args[0:]
        if n == 0:
            return acc
        else:
            return lambda: factorial((n - 1, n * acc))

    # noinspection PyPep8Naming
    def factorialM(args):
        n, acc = args[0:]
        if n < 0:
            return Failure(ValueError("%s must be greater than zero!" % n))
        else:
            ga = right(acc) if n == 0 else left((n - 1, n * acc))
            return Success(ga)

    _args = (1000, 1)
    assert Try.pure(trampoline(factorial, _args)) == Try.tailrecM(factorialM, _args)


if __name__ == '__main__':
    main()
