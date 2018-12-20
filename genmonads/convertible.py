import typing

from genmonads.mytypes import *


# noinspection PyUnresolvedReferences
class Convertible(Generic[A]):
    """
    A type that can be converted to and from pythonic lists.
    """

    def to_iterator(self) -> 'MIterator[A]':
        """
        Converts the `Convertible` into an iterator.

        Returns:
            genmonads.iterator.Iterator[A]: the resulting python iterator
        """
        from genmonads.iterator import Iterator as MIterator
        return MIterator.pure(*self.to_list())

    def to_list(self) -> typing.List[A]:
        """
        Converts the `Convertible` into a python list.

        Returns:
            typing.List[A]: the resulting python list
        """
        raise NotImplementedError

    def to_mlist(self) -> 'MList[A]':
        """
        Converts the `Convertible` into a monadic list.

        Returns:
            genmonads.mlist.List[A]: the resulting python list
        """
        from genmonads.mlist import List as MList
        return MList.pure(*self.to_list())

    def to_onel(self) -> 'Option[NonEmptyList[A]]':
        """
        Tries to convert the `Convertible` into a `NonEmptyList` monad.

        Returns:
            Option[NonEmptyList[A]]: the `NonEmptyList` wrapped in `Some` if
                                     the `List` is non-empty, `Nothing`
                                     otherwise
        """
        from genmonads.nel import onel
        return onel(*self.to_list())

    def to_stream(self) -> 'MStream[A]':
        """
        Converts the `Convertible` into a stream.

        Returns:
            genmonads.iterator.Stream[A]: the resulting Stream
        """
        from genmonads.iterator import Stream as MStream
        return MStream.pure(*self.to_list())
