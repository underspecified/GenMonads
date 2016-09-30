from genmonads.Monad import *


class Option(Monad):
    def __init__(self, *args, **kwargs):
        raise ValueError(
            "Tried to call the constructor of abstract base class Option. Use the option() function instead."
        )

    @staticmethod
    def from_value(value):
        if value is None:
            return None_()
        else:
            return Some(value)

    def __bool__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __mname__(self):
        return 'Option'

    def filter(self, f):
        raise NotImplementedError

    def flat_map(self, f):
        raise NotImplementedError

    def flatten(self):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def get_or_else(self, default):
        raise NotImplementedError

    def get_or_none(self):
        raise NotImplementedError

    def map(self, f):
        raise NotImplementedError


def option(value):
    return Option.from_value(value)


# noinspection PyMissingConstructor
class Some(Option):
    def __init__(self, value):
        self.value = value

    def __bool__(self):
        return True

    def __iter__(self):
        return MonadIter(self)

    def __str__(self):
        return 'Some(%s)' % self.value

    def flat_map(self, f):
        return self.map(f).flatten()

    def filter(self, f):
        return self if f(self.value) else None_()

    def flatten(self):
        return self.get()

    def get(self):
        return self.value

    def get_or_else(self, default):
        return self.value

    def get_or_none(self):
        return self.value

    def map(self, f):
        return Some(f(self.get()))


# noinspection PyMissingConstructor,PyPep8Naming
class None_(Option):
    # noinspection PyInitNewSignature
    def __init__(self):
        pass

    def __bool__(self):
        return False

    def __iter__(self):
        return MonadIter(self)

    def __str__(self):
        return 'None_()'

    def filter(self, f):
        return self

    def flat_map(self, f):
        return self

    def flatten(self):
        return self

    def get(self):
        raise ValueError("Tried to access the non-existent inner value of a None_ value")

    def get_or_else(self, default):
        return default

    def get_or_none(self):
        return None

    def map(self, f):
        return self


def main():
    print(do(x + y
             for x in option(2)
             if x < 10
             for y in option(5)
             if y % 2 != 0))

    def make_gen():
        for x in option(4):
            if x > 2:
                for y in option(10):
                    if y % 2 == 0:
                        yield x - y
    print(mfor(make_gen()))

    print(option(5) >> (lambda x: option(x * 2)))

    print(option(None).map(lambda x: x * 2))


if __name__ == '__main__':
    main()
