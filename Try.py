from Option import *


class Try(Monad):
    def __init__(self, thunk):
        self.thunk = thunk
        self._done = None

    def __iter__(self):
        return MonadIter(self)

    def __mname__(self):
        return 'Try'

    def eval(self):
        if not self._done:
            try:
                self._done = Success(self.thunk())
            except Exception as ex:
                self._done = Failure(ex)
        return self._done

    def filter(self, f):
        return self.eval() if self.eval() and f(self.get()) else Failure(TypeError("Filter failed!"))

    def flat_map(self, f):
        return self.map(f).flatten()

    def flatten(self):
        return Try(lambda: self.run().run())

    def get(self):
        self.eval().get()

    def get_or_else(self, default):
        # noinspection PyArgumentList
        return self.eval().get_or_else(default)

    def map(self, f):
        return Try(lambda: f(self.thunk()))

    def run(self):
        return self.eval().get()

    def to_option(self):
        return self.eval().to_option()


def try_to(thunk):
    return Try(thunk)


# noinspection PyMissingConstructor
class Success(Try):
    def __init__(self, result):
        self._result = result

    def __iter__(self):
        return MonadIter(self)

    def __bool__(self):
        return True

    def __str__(self):
        return 'Success(%s)' % self._result

    def map(self, f):
        return Success(f(self.get()))

    def flat_map(self, f):
        return self.map(f).flatten()

    def flatten(self):
        return self.get()

    def get(self):
        return self._result

    # noinspection PyUnusedLocal
    def get_or_else(self, default):
        return self._result

    def run(self):
        return self.get()

    def to_option(self):
        return Some(self._result)


# noinspection PyMissingConstructor
class Failure(Try):
    def __init__(self, ex):
        self._ex = ex

    def __iter__(self):
        return MonadIter(self)

    def __bool__(self):
        return False

    def __str__(self):
        return 'Failure(%s)' % self._ex

    def map(self, f):
        return self

    def flat_map(self, f):
        return self

    def flatten(self):
        return self

    def get(self):
        raise self._ex

    def get_or_else(self, default):
        return default

    def run(self):
        raise self.get()

    def to_option(self):
        return None_()


def main():
    print(do(x + y
             for x in Try(2)
             if x < 10
             for y in Try(5)
             if y % 2 != 0))

    def make_gen():
        for x in Try(4):
            if x > 2:
                for y in Try(10):
                    if y % 2 == 0:
                        yield x - y
    print(do(make_gen()))

    print(Try(5) >> (lambda x: Try(x * 2)))

    print(Try(None).map(lambda x: x * 2))


if __name__ == '__main__':
    main()
