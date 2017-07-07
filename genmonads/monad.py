import re
import sys

from pony.orm.decompiling import decompile

from genmonads.applicative import Applicative
from genmonads.flat_map import FlatMap
from genmonads.gettable import Gettable
from genmonads.monadtrans import ast2src

__all__ = ['Monad', 'do', 'mfor']


class Monad(Applicative, FlatMap, Gettable):
    """
    A base class for representing monads.

    Monadic computing is supported with `map()` and `flat_map() functions, and for-comprehensions can be formed
    by evaluating generators over monads with the `mfor()` function.
    """

    def ap(self, ff):
        """
        Applies a function in the applicative functor to a value in the applicative functor.

        Args:
            ff (Applicative[Callable[[A],B]]): the function in the applicative functor

        Returns:
            Applicative[B]: the resulting value in the applicative functor
        """
        self.flat_map(lambda a: ff.map(lambda f: f(a)))

    def __iter__(self):
        """
        Returns:
            MonadIter: an iterator over the content of the monad to support usage in generators
        """
        return MonadIter(self)

    @staticmethod
    def __mname__():
        """
        Returns:
            str: the name of the type class
        """
        return 'Monad'

    def __rshift__(self, f):
        """
        A symbolic alias for `flat_map()`. Uses dynamic type checking to permit arguments of the forms
         `self >> lambda x: Monad(x)` and `self >> Monad(x)`.

        Args:
            f (Union[Callable[[A],Monad[B]],Monad[B]]): the function to apply

        Returns:
            Monad[B]
        """
        return f if isinstance(f, Monad) else self.flat_map(f)

    def flat_map(self, f):
        """
        Applies a function that produces an Monad from unwrapped values to an Monad's inner value and flattens the
        nested result.

        Equivalent to `self.map(f).flatten()`.

        Args:
            f (Callable[[A],Monad[B]]): the function to apply

        Returns:
            Monad[B]: the resulting monad
        """
        raise NotImplementedError

    def get(self):
        """
        Returns the `Monad`'s inner value.
        
        Returns:
            T: the inner value
        """
        raise NotImplementedError

    def map(self, f):
        """
        Applies a function to the inner value of a monad.

        Args:
            f (Callable[[A],B]): the function to apply

        Returns:
            Monad[B]: the resulting monad
        """
        return self.flat_map(lambda a: self.pure(f(a)))

    @staticmethod
    def pure(value):
        """
        Injects a value into the monad.

        Args:
            value (T): the value

        Returns:
            Monad[T]: the monadic value
        """
        raise NotImplementedError


class MonadIter(object):
    """
    An iterator wrapper class over the content of the monad to support usage in generators
    """
    def __init__(self, monad):
        self.monad = monad

    def __next__(self):
        raise(TypeError('Use mfor(...) function for evaluation'))

    next = __next__


# noinspection PyShadowingBuiltins,PyProtectedMember
def mfor(gen, frame_depth=5):
    """The monadic for-comprehension
    Evaluates a generator over a monadic value, translating it into the equivalent for-comprehension.

    Args:
        gen (Generator[T, None, None]): a generator over a monadic value
        frame_depth (int): the frame depth of which to search for the outermost monad

    Returns:
        Monad[T]: the for-comprehension that corresponds to the generator
    """
    try:
        # decompile the generator into AST, externally referenced names, and memory cells
        ast_, external_names, cells = decompile(gen)
        #print('ast:', ast_, file=sys.stderr)
        #print('external_names:', external_names, file=sys.stderr)
        #print('globals:', gen.gi_frame.f_globals, file=sys.stderr)

        # for generator expressions, the out-most monad is evaluated, converting it into a MonadIter
        # it is referred to by the symbol .0 in the generator's bytecode, so we need to retrieve the original monad
        # for generator functions, the original monad is preserved in unevaluated form, so we use the monad class as
        # a dummy value
        monad = gen.gi_frame.f_locals['.0'].monad if '.0' in gen.gi_frame.f_locals else Monad
        code = re.sub(r'''^\.0''', 'monad', ast2src(ast_))
        #print('code:', code, file=sys.stderr)

        # next we insert the original monad into the code's locals and return the results of its evaluation
        i = frame_depth
        while i >= 0:
            # noinspection PyBroadException,PyUnusedLocal
            try:
                globals = sys._getframe(i).f_globals
                locals = sys._getframe(i).f_locals
                locals['monad'] = monad
                #print('code:', code, file=sys.stderr)
                #print('globals:', globals, file=sys.stderr)
                #print('locals:', locals, file=sys.stderr)
                return eval(code, globals, locals)
            except Exception as ex:
                #print(type(ex), ex, file=sys.stderr)
                i -= 1
        if i < 0:
            raise ValueError("Monad not found in generator locals at frame depth %d!" % frame_depth)
    except Exception as ex:
        raise ex


def do(gen, frame_depth=10):
    """
    A synonym for `mfor`.

    Evaluates a generator over a monadic value, translating it into the equivalent for-comprehension.

    Args:
        gen (Generator[T, None, None]): a generator over a monadic value
        frame_depth (int): the frame depth of which to search for the outermost monad

    Returns:
        Monad[T]: the for-comprehension that corresponds to the generator
    """
    mfor(gen, frame_depth)
