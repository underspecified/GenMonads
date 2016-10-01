# noinspection PyUnresolvedReferences
from genmonads.Monad import *
from genmonads.Option import *


class Try(Monad):
    def __init__(self, *args, **kwargs):
        raise ValueError(
            "Tried to call the constructor of abstract base class Try. Use the try_to() function instead."
        )

    def __bool__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __mname__(self):
        return 'Try'

    def filter(self, f):
        raise NotImplementedError

    def flat_map(self, f):
        raise NotImplementedError

    def flatten(self):
        raise NotImplementedError

    @staticmethod
    def from_thunk(thunk):
        try:
            return Success(thunk())
        except Exception as e:
            return Failure(e)

    def get(self):
        raise NotImplementedError

    def get_or_else(self, default):
        raise NotImplementedError

    def map(self, f):
        raise NotImplementedError

    def to_option(self):
        raise NotImplementedError


def try_to(thunk):
    return Try.from_thunk(thunk)


# noinspection PyMissingConstructor
class Success(Try):
    def __init__(self, result):
        self._result = result

    def __bool__(self):
        return True

    def __eq__(self, other):
        if isinstance(other, Success):
            return self.get().__eq__(other.get())
        return False

    def __iter__(self):
        return MonadIter(self)

    def __mname__(self):
        return 'Try'

    def __str__(self):
        return 'Success(%s)' % self._result

    def filter(self, f):
        return self.flat_map(lambda x: Success(x) if f(x) else Failure(ValueError("Filter failed!")))

    def flat_map(self, f):
        return self.map(f).flatten()

    def flatten(self):
        return self.get()

    def get(self):
        return self._result

    # noinspection PyUnusedLocal
    def get_or_else(self, default):
        return self._result

    def map(self, f):
        return Try.from_thunk(lambda: f(self.get()))

    def to_option(self):
        return Some(self._result)


# noinspection PyMissingConstructor
class Failure(Try):
    def __init__(self, ex):
        self._ex = ex

    def __bool__(self):
        return False

    def __eq__(self, other):
        if isinstance(other, Success):
            return self.get().__eq__(other.get())
        return False

    def __iter__(self):
        return MonadIter(self)

    def __str__(self):
        return 'Failure(%s)' % self._ex

    def __mname__(self):
        return 'Try'

    def filter(self, f):
        return self

    def flat_map(self, f):
        return self

    def flatten(self):
        return self

    def get(self):
        return self._ex

    def get_or_else(self, default):
        return default

    def map(self, f):
        return self

    def raise_ex(self):
        raise self._ex

    def to_option(self):
        return Nothing()


def main():
    print(do(x + y
             for x in try_to(lambda: 2)
             if x < 10
             for y in try_to(lambda: 5)
             if y % 2 != 0))

    def make_gen():
        for x in try_to(lambda: 4):
            if x > 2:
                for y in try_to(lambda: 10):
                    if y % 2 == 0:
                        yield x - y
    print(do(make_gen()))

    print((try_to(lambda: 5) >> (lambda x: try_to(lambda: 2))))

    print(try_to(lambda: 1 / 0).map(lambda x: x * 2))


if __name__ == '__main__':
    main()
