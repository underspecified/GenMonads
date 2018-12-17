from genmonads.mytypes import *


class Cartesian(Generic[A]):
    """
    A type class to construct products from type classes.
    
    Allows functors and applicatives to work with functions of arbitrary arity.
    """

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the name of the type class
        """
        return 'Cartesian'

    def product(self,
                fb: 'Cartesian[[Tuple[A, B]]]'
                ) -> 'Cartesian[[Tuple[A, B]]]':
        """
        Constructs a cartesian of the product of the inner values of two
        cartesians.

        Args:
            fb (Cartesian): the second cartesian

        Returns:
            Cartesian[(A, B)]: the resulting cartesian
        """
        raise NotImplementedError
