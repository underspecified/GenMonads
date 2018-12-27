from genmonads.match import match, matches
from genmonads.mytypes import *

__all__ = ['Gettable', ]


class Gettable(Container[A]):
    """
    A type that represents a wrapped value with a `get()` accessor function.

    This type is useful for implementing monads in python because it lacks the
    access to inner values provided by pattern matching.
    """

    def __bool__(self) -> bool:
        return self.is_gettable()

    def __contains__(self, elem: A) -> bool:
        """
        Checks if any of this monad's inner values is equivalent to `elem`.

        Args:
            elem (A): the element

        Returns:
            bool: True if any of this monad's inner values is equivalent to
                  `elem`
        """
        return self.get() == elem

    def get(self) -> A:
        """
        Returns the `Gettable`'s inner value.

        Returns:
            A: the inner value
        """
        raise NotImplementedError

    def get_or_else(self, default: A) -> A:
        """
        Returns the `Gettable`'s inner value if defined or `default` otherwise.

        Args:
            default (A): the value to return for `Nothing` instances

        Returns:
            A: the `Gettable`'s inner value if defined or `default` otherwise
        """
        return self.get() if self else default

    def get_or_none(self) -> Optional[A]:
        """
        Returns the `Gettable`'s inner value if defined or `None` otherwise.

        Provided as interface to code that expects `None` values.

        Returns:
            Optional[A]: the `Gettable`'s inner value if defined or `None`
            otherwise
        """
        return self.get_or_else(None)

    # noinspection PyMethodMayBeStatic
    def is_gettable(self) -> bool:
        """
        Returns true if this type class implements the `get()` method.

        Returns:
            bool: `True` if `get()` is implemented, `False` otherwise
        """
        return True

    # noinspection PyProtectedMember,PyUnresolvedReferences
    def match(self, conditions: Dict['Gettable[A]', F1[A, B]]) -> Optional[B]:
        """
        Checks a `Gettable[A]` type class instance `x` against dictionary of
        pattern => action mappings, and when a match is found, returns the
        results from calling the associated action on `x`'s inner value.
        Wildcard matches (`_`) are supported in both the type class and inner
        values.

        >>> from genmonads.match import _
        >>> from genmonads.option import Some, Nothing, option
        >>> x = option(5)
        >>> x.match({
        >>>     Some(5-1):
        >>>         lambda y: print("Some(5-1) matches %s: %s" % (x, y)),
        >>>     Some(_):
        >>>         lambda y: print("Some(_) matches %s: %s" % (x, y)),
        >>>     Nothing():
        >>>         lambda: print("Nothing() matches:", x),
        >>>     _:
        >>>         lambda: print("Fallthrough wildcard matches:", x),
        >>> })
        Some(_) matches Some(5): 5

        Args:
            conditions (Dict[Gettable[A], F1[A, B]]): a dictionary of
                                                      pattern => action mappings

        Returns:
            Optional[B]: the result of calling the matched action on `x`'s
                         inner value or `None` if no match is found
        """
        return match(self, conditions)

    def matches(self, other: 'Gettable[B]') -> bool:
        """
        Checks if `self` matches `other`, taking into account wildcards in both
        type classes and arguments.

        Args:
            other (Gettable[B]): the type class to match against

        Returns:
            bool: True if `self` matches `other`, False otherwise
        """
        return matches(self, other)

    def unpack(self) -> Tuple[A, ...]:
        """
        Returns the `Gettable`'s inner value as a tuple to support unpacking

        Returns:
            Tuple[A]: the inner value
        """
        return self.get(),
