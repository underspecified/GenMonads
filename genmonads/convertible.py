import typing

from genmonads.mytypes import *


# noinspection PyUnresolvedReferences
class Convertible(Generic[A]):
    """
    A type that can be converted to and from pythonic lists.
    """

    def to_iter(self) -> typing.Iterator[A]:
        """
        Converts the `Convertible` into a python iterator.

        Returns:
            typing.Iterator[A]: the resulting python iterator
        """
        raise NotImplementedError

    def to_miter(self) -> 'Iterator[A]':
        """
        Converts the `Convertible` into a monadic iterator.

        Returns:
            genmonads.iterator.Iterator[A]: the resulting monadic iterator
        """
        from genmonads.iterator import Iterator
        return Iterator.from_iter(self.to_iter())

    def to_list(self) -> typing.List[A]:
        """
        Converts the `Convertible` into a python list.

        Returns:
            typing.List[A]: the resulting python list
        """
        return [x for x in self.to_iter()]

    def to_mlist(self) -> 'List[A]':
        """
        Converts the `Convertible` into a monadic list.

        Returns:
            genmonads.mlist.List[A]: the resulting python list
        """
        from genmonads.mlist import List
        return List.pure(*self.to_iter())

    def to_onel(self) -> 'Option[NonEmptyList[A]]':
        """
        Tries to convert the `Convertible` into a `NonEmptyList` monad.

        Returns:
            Option[NonEmptyList[A]]: the `NonEmptyList` wrapped in `Some` if
                                     the `List` is non-empty, `Nothing`
                                     otherwise
        """
        from genmonads.nel import onel
        return onel(*self.to_iter())

    def to_par_list(self) -> 'ParList[A]':
        from genmonads.par_list import ParList
        return ParList.from_iterator(self.to_iter())

    def to_stream(self) -> 'Stream[A]':
        """
        Converts the `Convertible` into a stream.

        Returns:
            genmonads.iterator.Stream[A]: the resulting Stream
        """
        from genmonads.iterator import Stream
        return Stream.from_iter(self.to_iter())
