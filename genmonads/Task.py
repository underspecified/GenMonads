# noinspection PyUnresolvedReferences
from typing import TypeVar

# noinspection PyUnresolvedReferences
from genmonads.Monad import *
from genmonads.Try import *

A = TypeVar('A')
B = TypeVar('B')
T = TypeVar('T')


class Task(Monad):
    def __init__(self, thunk):
        self.thunk = thunk
        self._done = Try.empty()

    def __mname__(self):
        return 'Task'

    def eval(self):
        if not self._done:
            self._done = Try(self.thunk)
        return self._done

    def flatten(self):
        return self.flat_map(lambda x: x if isinstance(x, Task) else Task.pure(lambda: x.run()))

    def map(self, f):
        return Task.pure(lambda: f(self.thunk()))

    @staticmethod
    def pure(thunk):
        return Task(thunk)

    def run(self):
        return self.eval().get()

    def to_option(self):
        return self.to_try().to_option()

    def to_try(self):
        return self.eval()


def task(thunk):
    return Task.pure(thunk)


def main():
    pass


if __name__ == '__main__':
    main()
