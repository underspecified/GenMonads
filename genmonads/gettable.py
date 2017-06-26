from genmonads.match import *

__all__ = ['Gettable', 'Wildcard', 'is_wildcard', 'match', 'matches', '_']


class Gettable:
    """
    A type that represents a wrapped value with a `get()` accessor function.

    This type is useful for implementing monads in python because it lacks the access to inner values
    provided by pattern matching.
    """

    def get(self):
        """
        Returns the `Gettable`'s inner value.
        Returns:
            T: the inner value
        """
        raise NotImplementedError

    def get_or_else(self, default):
        """
        Returns the `Gettable`'s inner value if defined or `default` otherwise.

        Args:
            default (T): the value to return for `Nothing` instances

        Returns:
            T: the `Gettable`'s inner value if defined or `default` otherwise
        """
        return self.get() if self.is_gettable() else default

    def get_or_none(self):
        """
        Returns the `Gettable`'s inner value if defined or `None` otherwise.

        Provided as interface to code that expects `None` values.

        Returns:
            Union[T,None]: the `Gettable`'s inner value if defined or `None` otherwise
        """
        return self.get_or_else(None)

    def forall(self, p):
        return True if self.is_gettable() or p(self.get()) else False

    def is_gettable(self):
        """
        Returns true if this type class implements the `get()` method.
        Returns:
            Boolean: `True` if `get()` is implemented, `False` otherwise
        """
        return True

    def match(self, conditions):
        """
        Checks a `Gettable[A]` type class instance `x` against dictionary of pattern => action mappings, and when a
        match is found, returns the results from calling the associated action on `x`'s inner value. Wildcard matches
        (`_`) are supported in both the type class and inner values.

        >>> from genmonads.match import match, _
        >>> from genmonads.option import Some, Nothing, option
        >>> x = option(5)
        >>> x.match({
        >>>     Some(5-1):
        >>>         lambda y: print("Some(5-1) matches %s: %s" % (x, y)),
        >>>     Some(_):
        >>>         lambda y: print("Some(5-1) matches %s: %s" % (x, y)),
        >>>     Nothing():
        >>>         lambda: print("Nothing() matches", x),
        >>>     _:
        >>>         lambda: print("Fallthrough wildcard match:", x),
        >>>})
        Some(_) matches Some(5): 5

        Args:
            x (Gettable[A]): the type class to match against
            conditions (Dict[Gettable[A],Callable[[A],B]): a dictionary of pattern => action mappings

        Returns:
            Union[B,None]: the result of calling the matched action on `x`'s inner value or `None` if no match is found
        """
        return match(self, conditions)

    def matches(self, other):
        return matches(self, other)

    def unpack(self):
        """
        Returns the `Gettable`'s inner value as a tuple to support unpacking
        Returns:
            Tuple[T]: the inner value
        """
        return self.get(),
