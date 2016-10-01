# noinspection PyUnresolvedReferences
from genmonads.Monad import *
from genmonads.Option import *


class Task(Monad):
    def __init__(self, thunk):
        self.thunk = thunk
        self._done = Nothing()

    def __iter__(self):
        return MonadIter(self)

    def __mname__(self):
        return 'Task'

    def eval(self):
        if not self._done:
            self._done = Some(self.thunk())
        return self._done

    def filter(self, f):
        #return self.flat_map(lambda x: Task(lambda: x) if f(x) else Task(lambda: Nothing())
        raise NotImplementedError

    def flat_map(self, f):
        return self.map(f).flatten()

    def flatten(self):
        return Task(lambda: self.run().run())

    def map(self, f):
        return Task(lambda: f(self.thunk()))

    def run(self):
        return self.eval().get()


def task(thunk):
    return Task(thunk)


def main():
    pass


if __name__ == '__main__':
    main()
