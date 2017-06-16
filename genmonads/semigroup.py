class Semigroup(object):
    """
    A type class representing semigroups."""

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'Semigroup'

    def combine(self, other):
        raise NotImplementedError
