import re
import sys

from pony.orm.asttranslation import *
from pony.orm.decompiling import decompile


class Monad(object):
    def __iter__(self):
        raise NotImplementedError

    def __mname__(self):
        return 'Monad'

    def __rshift__(self, f):
        return self.flat_map(f)

    def flat_map(self, f):
        raise NotImplementedError

    def map(self, f):
        raise NotImplementedError

    def filter(self, f):
        raise NotImplementedError

    def flatten(self):
        raise NotImplementedError


class MonadIter(object):
    def __init__(self, monad):
        self.monad = monad

    def __next__(self):
        raise(TypeError('Use mfor(...) function for iteration' % self.monad.__mname__))

    next = __next__


# noinspection PyPep8Naming,PyMethodMayBeStatic
class MonadTranslator(PythonTranslator):
    def postGenExpr(self, node):
        return node.code.src

    def postGenExprInner(self, node):
        qual_src = [qual.src for qual in node.quals]
        if qual_src:
            qual_src[-1] = qual_src[-1].replace('.flat_map', '.map')
        return ''.join(qual_src) + node.expr.src + ')' * len(node.quals)

    def postGenExprFor(self, node):
        src = node.iter.src
        src += ''.join('.filter(lambda %s: %s)' % (node.assign.src, if_.test.src) for if_ in node.ifs)
        src += '.flat_map(lambda %s: ' % node.assign.src
        return src

    def postLambda(self, node):
        #print('postLambda:', node, file=sys.stderr)
        src = 'lambda %s: %s' % (','.join(node.argnames), node.code.src)
        #print('src:', src, file=sys.stderr)
        return src


def ast2src(tree):
    MonadTranslator(tree)
    return tree.src


# noinspection PyShadowingBuiltins,PyProtectedMember
def mfor(gen, frame_depth=1):
    try:
        ast_, external_names, cells = decompile(gen)
        #print('ast:', ast_, file=sys.stderr)
        #print('external_names:', external_names, file=sys.stderr)
        #print('globals:', gen.gi_frame.f_globals, file=sys.stderr)
        monad = gen.gi_frame.f_locals['.0'].monad if '.0' in gen.gi_frame.f_locals else Monad
        code = re.sub(r'''^\.0''', 'monad', ast2src(ast_))
        #print('code:', code, file=sys.stderr)
        globals = sys._getframe(frame_depth).f_globals
        locals = sys._getframe(frame_depth).f_locals
        locals['monad'] = monad
        return eval(code, globals, locals)
    except Exception as e:
        raise e


do = mfor
