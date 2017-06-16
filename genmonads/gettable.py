__all__ = ['Gettable', ]


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
        raise NotImplementedError

    def is_empty(self):
        return not self.is_gettable()

    def non_empty(self):
        return self.is_gettable()
