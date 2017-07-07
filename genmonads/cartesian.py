__all__ = ['Cartesian', ]


class Cartesian:
    """
    A type class to construct products from type classes.
    
    Allows functors and applicatives to work with functions of arbitrary arity.
    """

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'Cartesian'

    def product(self, fb):
        """
        Constructs a cartesian of the product of the inner values of two cartesians.

        Args:
            fb (Cartesian): the second cartesian

        Returns:
            Cartesian[(A,B)]: the resulting cartesian
        """
        raise NotImplementedError
