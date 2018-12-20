#from dataclasses import dataclass
import re
import sys

from pony.orm.decompiling import decompile

from genmonads.monad import Monad
from genmonads.monadtrans import ast2src
from genmonads.mytypes import *

__all__ = ['do', 'mfor']


# noinspection PyShadowingBuiltins,PyProtectedMember
def mfor(gen: Generator[T, None, None], frame_depth: int = 10):
    """The monadic for-comprehension
    Evaluates a generator over a monadic value, translating it into the
    equivalent for-comprehension.

    Args:
        gen (Generator[T, None, None]): a generator over a monadic value
        frame_depth (int): the frame depth of which to search for the outermost
                           monad

    Returns:
        Monad[T]: the for-comprehension that corresponds to the generator
    """
    try:
        # decompile the generator into AST, externally referenced names, and
        # memory cells
        ast_, external_names, cells = decompile(gen)
        #print('ast:', ast_, file=sys.stderr)
        #print('external_names:', external_names, file=sys.stderr)
        #print('globals:', gen.gi_frame.f_globals, file=sys.stderr)

        # for generator expressions, the out-most monad is evaluated,
        # converting it into a MonadIter
        #
        # it is referred to by the symbol .0 in the generator's bytecode,
        # so we need to retrieve the original monad for generator functions,
        # the original monad is preserved in unevaluated form, so we use the
        # monad class as a dummy value
        if '.0' in gen.gi_frame.f_locals:
            monad = gen.gi_frame.f_locals['.0'].monad
        else:
            monad = Monad
        code = re.sub(r'''^\.0''', 'monad', ast2src(ast_))
        #print('code:', code, file=sys.stderr)

        # next we insert the original monad into the code's locals and return
        # the results of its evaluation
        i = frame_depth
        while i >= 0:
            # noinspection PyBroadException,PyUnusedLocal
            try:
                globals = sys._getframe(i).f_globals
                locals = sys._getframe(i).f_locals
                locals['monad'] = monad
                #print('code@%d:' % i, code, file=sys.stderr)
                #print('globals@%d:' % i, globals, file=sys.stderr)
                #print('locals@%d:' % i, locals, file=sys.stderr)
                return eval(code, globals, locals)
            except Exception as ex:
                #print('Exception@%d' % i, type(ex), ex, file=sys.stderr)
                i -= 1
        if i < 0:
            raise ValueError(
                "Monad not found in generator locals at frame depth %d!" %
                frame_depth)
    except Exception as ex:
        raise ex


def do(gen: Generator[T, None, None], frame_depth: int = 10):
    """
    A synonym for `mfor`.

    Evaluates a generator over a monadic value, translating it into the
    equivalent for-comprehension.

    Args:
        gen (Generator[T, None, None]): a generator over a monadic value
        frame_depth (int): the frame depth of which to search for the outermost
                           monad

    Returns:
        Monad[T]: the for-comprehension that corresponds to the generator
    """
    mfor(gen, frame_depth)
