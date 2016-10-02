import re
import sys

from pony.orm.decompiling import decompile

from genmonads.MonadTrans import ast2src


class Monad(object):
    """
    A base class for representing monads.

    Monadic computing is supported with map, flat_map, and flatten functions, and for-comprehensions can be formed by
    evaluating generators over monads with the mfor function.
    """

    def __iter__(self):
        """
        Returns:
            MonadIter: an iterator over the content of the monad to support usage in generators
        """
        return MonadIter(self)

    def __mname__(self):
        """
        Returns:
            str: the monad's name
        """
        return 'Monad'

    def __rshift__(self, f):
        """
        A symbolic alias for flat_map.

        Args:
            f (Callable[[A],Monad[B]]): the function to apply

        Returns:
            Monad[B]
        """
        return self.flat_map(f)

    def filter(self, f):
        """
        Args:
            f (Callable[[T],bool]): the predicate

        Returns:
            Option[T]: this instance if the predicate is true when applied to its inner value, Nothing otherwise
        """
        raise NotImplementedError

    def flat_map(self, f):
        """
        Applies a function that produces an Monad from unwrapped values to an Monad's inner value and flattens the
        nested result. Equivalent to self.map(f).flatten()

        Args:
            f (Callable[[A],Monad[B]]): the function to apply

        Returns:
            Monad[B]: the resulting monad
        """
        raise NotImplementedError

    def flatten(self):
        """
        Flattens nested instances of Monad. Equivalent to self.flat_map(lambda x: Monad.pure(x))

        Returns:
            Monad[T]: the flattened monad
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
        raise NotImplementedError

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
def mfor(gen, frame_depth=1):
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

        # for generator expressions, the outmost monad is evaluated, converting it into a MonadIter
        # it is referred to by the symbol .0 in the generator's bytecode, so we need to retrieve the original monad
        # for generator functions, the original monad is preserved in unevaluated form, so we use the monad class as
        # a dummy value
        monad = gen.gi_frame.f_locals['.0'].monad if '.0' in gen.gi_frame.f_locals else Monad
        code = re.sub(r'''^\.0''', 'monad', ast2src(ast_))
        #print('code:', code, file=sys.stderr)

        # next we insert the original monad into the code's locals and return the results of its evaluation
        globals = sys._getframe(frame_depth).f_globals
        locals = sys._getframe(frame_depth).f_locals
        locals['monad'] = monad
        return eval(code, globals, locals)
    except Exception as e:
        raise e


def do(gen, frame_depth=1):
    """A synonym for mfor
    Evaluates a generator over a monadic value, translating it into the equivalent for-comprehension.

    Args:
        gen (Generator[T, None, None]): a generator over a monadic value
        frame_depth (int): the frame depth of which to search for the outermost monad

    Returns:
        Monad[T]: the for-comprehension that corresponds to the generator
    """
    mfor(gen, frame_depth)
