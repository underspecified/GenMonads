from typing import *

__all__ = ['Any', 'Callable', 'Container', 'Dict', 'Generator', 'Generic',
           'Optional', 'Tuple', 'Type', 'TypeVar', 'Union',
           'T', 'A', 'AA', 'B', 'BB', 'C', 'F0', 'F1', 'F2',
           'FoldLeft', 'FoldRight', 'Predicate', 'Thunk']

T = TypeVar('T')
A = TypeVar('A')
AA = TypeVar('AA')
B = TypeVar('B')
BB = TypeVar('BB')
C = TypeVar('C')

F0 = Callable[[], A]
F1 = Callable[[A], B]
F2 = Callable[[A, B], C]

FoldLeft = F2[B, A, B]
FoldRight = F2[A, B, B]
Predicate = F1[T, bool]
Thunk = F0[T]
