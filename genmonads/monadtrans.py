from pony.orm.asttranslation import PythonTranslator
# noinspection PyUnresolvedReferences
from pony.thirdparty.compiler.ast import *


# noinspection PyPep8Naming,PyMethodMayBeStatic
class MonadTranslator(PythonTranslator):
    # noinspection PyUnresolvedReferences
    """
    The translator class that converts the AST of a generator over monads into a series of nested calls to
    `flat_map()`, `map()`, and `filter()`.

    For example, consider the following generator:

    >>> from genmonads.option import *
    >>> print(mfor(x + y
              for x in option(2)
              if x < 10
              for y in option(5)
              if y % 2 != 0))
    Some(7)

    The above generator is automatically translated into the following at run-time:

    >>> print(option(2)
                  .filter(lambda x: x < 10)
                  .flat_map(lambda x: option(5)
                      .filter(lambda y: y % 2 != 0)
                      .map(lambda y: x + y)))
    Some(7)
    """

    def postGenExpr(self, node):
        """
        Converts the AST node for the full generator expression into its code representation.

        Responsible for discarding the parentheses around the generator expression.

        Args:
            node (GenExpr): the AST node

        Returns:
            str: the source code representation
        """
        return node.code.src

    def postGenExprInner(self, node):
        """
        Converts the AST node for the generator's inner expression into its code representation.

        Responsible for converting the final `flat_map` call into a call to `map` and adding closing parentheses.

        Args:
            node (GenExprInner): the AST node

        Returns:
            str: the source code representation
        """
        qual_src = [qual.src for qual in node.quals]
        if qual_src:
            qual_src[-1] = qual_src[-1].replace('.flat_map', '.map')
        return ''.join(qual_src) + node.expr.src + ')' * len(node.quals)

    def postGenExprFor(self, node):
        """
        Converts the AST node for the body of a generator's `for` statements into its code representation.

        Responsible for converting `if` statements into calls to `filter` and `for x in y` in to calls to `flat_map`.

        Args:
            node (GenExprFor): the AST node

        Returns:
            str: the source code representation
        """
        src = node.iter.src
        src += ''.join('.filter(lambda %s: %s)' % (node.assign.src, if_.test.src) for if_ in node.ifs)
        src += '.flat_map(lambda %s: ' % node.assign.src
        return src

    def postLambda(self, node):
        """Converts the AST node for a lambda expression into its code representation

        Args:
            node (Lambda): the AST node

        Returns:
            str: the source code representation
        """
        src = 'lambda %s: %s' % (','.join(node.argnames), node.code.src)
        return src


def ast2src(tree):
    """
    Converts an AST into python source, replacing generator expressions into a series of nested calls to `flat_map`,
    `map`, and `filter` by applying the `MonadTranslator` to an AST.

    Args:
        tree (GenExpr): the AST node of a generator expression

    Returns:
        str: the source code representation
    """
    MonadTranslator(tree)
    # noinspection PyUnresolvedReferences
    return tree.src
