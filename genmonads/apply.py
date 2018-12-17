from genmonads.cartesian import Cartesian
from genmonads.functor import Functor
from genmonads.mytypes import *

__all__ = ['Apply', ]


class Apply(Functor,
            Cartesian,
            Generic[A],):
    """
    The applicative functor without pure().
    """

    @staticmethod
    def __mname__() -> str:
        """
        Returns:
            str: the name of the type class
        """
        return 'Apply'

    def ap(self,
           ff: Callable[['Apply[A]'], 'Apply[B]']
           ) -> 'Apply[B]':
        """
        Applies a function over applicative functors to a value inside the
        applicative functor.

        Args:
            ff (Callable[[Apply[A]], Apply[B]]): the function to apply

        Returns:
            Apply[B]: the resulting applicative functor
        """
        raise NotImplementedError

    def ap2(self,
            fb: 'Apply[B]',
            ff: Callable[['Apply[Tuple[A, B]]'], 'Apply[C]']
            ) -> 'Apply[C]':
        """
        Applies a function over applicative functors of arity two to a value
        inside the applicative functor.

        Args:
            fb (Apply[B]): the second argument to the function
            ff (Callable[[Apply[(A, B)]], Apply[C]]): the function to apply

        Returns:
            Apply[C]: the resulting applicative functor
        """
        def go(a_b_f):
            a, (b, f) = a_b_f
            return f(a, b)
        return self.product(fb.product(ff)).map(go)

    def map(self, f: Callable[[A], B]) -> 'Apply[B]':
        """
        Applies a function to the inner value of an applicative functor.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Apply[B]: the resulting applicative functor
        """
        raise NotImplementedError

    def map2(self,
             fb: 'Apply[B]',
             f: Callable[[A, B], 'Apply[C]']
             ) -> 'Apply[C]':
        """
        Applies a function of arity two to a value inside the applicative
        functor.

        Args:
            fb (Apply[B]): the second argument to the function
            f (Callable[(A, B)], Apply[C]]): the function to apply

        Returns:
            Apply[C]: the resulting applicative functor
        """
        def go(a_b: Tuple[A, B]) -> 'Apply[C]':
            a, b = a_b
            return f(a, b)
        return self.product(fb).map(go)

    def map2_eval(self,
                  fb: 'Apply[Eval[B]]',
                  f: Callable[[Tuple[A, 'Eval[B]']], 'Apply[C]']
                  ) -> 'Apply[C]':
        """
        Applies a function of arity two to a value inside the applicative
        functor using Eval to support lazy evaluation.

        Args:
            fb (Apply[Eval[B]]): the second argument to the function
            f (Callable[(A,Eval[B])],Apply[C]]): the function to apply

        Returns:
            Apply[C]: the resulting applicative functor
        """
        from genmonads.eval import Eval
        return fb.map(lambda _fb: self.map2(_fb, f))

    def product(self, fb: 'Apply[B]') -> 'Apply[Tuple[A, B]]':
        """
        Constructs an applicative functor of the product of the inner values of
        two applicative functors.

        Args:
            fb (Apply[B]): the second applicative functor

        Returns:
            Apply[(A,B)]: the resulting applicative functor
        """
        return fb.ap(self.map(lambda a: lambda b: (a, b)))
