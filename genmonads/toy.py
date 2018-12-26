import functools
import typing
from multiprocessing import cpu_count

from multiprocess.pool import *
# noinspection PyUnresolvedReferences
from dill.detect import baditems
import dill

from genmonads.eval import always, Eval
from genmonads.mytypes import *

#dill.settings['recurse'] = True


class LazyPool(Generic[A]):
    def __init__(self, thunk: Thunk[Pool]):
        self._value = thunk

    def map_with(self, f: F1[A, B], _input: typing.List[A]) -> typing.List[B]:
        with self._value() as pool:
            output = pool.map(f, _input)
        return list(output)


class ParList(Generic[A]):
    # noinspection PyUnusedLocal
    def __init__(self, *values: A, pool, workers=cpu_count()):
        #print("init.values:", values)
        self.values: typing.List[A] = [v for v in values]
        self.workers = workers
        self.pool = pool

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __repr__(self) -> str:
        return 'ParList(%s)' % ', '.join(str(v) for v in self.values)

    def map(self, f: F1[A, B]) -> 'ParList[B]':
        return self.flat_map(lambda a: ParList(f(a), pool=self.pool))

    def flat_map(self, func: F1[A, 'ParList[B]']) -> 'ParList[B]':
        values: typing.Iterable[B] = self.pool.map(func, self.values)
        print("values:", values)
        return ParList(*[v
                         for vs in values
                         for v in vs.values], pool=self.pool)

    @staticmethod
    def pure(*values: A, pool) -> 'ParList[A]':
        return ParList(*values, pool=pool)


def main():
    my_pool = Pool()
    print(ParList(4, 5, 6, pool=my_pool).map(lambda x: x + 1))
    print(ParList(1, 2, 3, pool=my_pool)
          .flat_map(lambda x: ParList(4, 5, 6, pool=my_pool)
                    .map(lambda y: x + y)))


if __name__ == '__main__':
    main()
