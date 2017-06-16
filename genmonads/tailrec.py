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

    print(trampoline(factorial, 1000))


if __name__ == '__main__':
    main()
