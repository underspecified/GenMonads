from types import GeneratorType, LambdaType
import inspect

__all__ = ['arity', 'is_lambda', 'is_thunk']


def arity(f):
    """
    Returns the arity, or number of arguments of function `f`.

    Args:
        f (Callable[..., B]): the function to check

    Returns:
        int: the arity of `f`
    """
    sig = inspect.signature(f)
    return len(sig.parameters)


def is_generator(it):
    """
    Checks if iterable `it` is a generator.

    Args:
        it (Iterable[T]): the function to check

    Returns:
        bool: True if `it` is a generator, False otherwise
    """
    return isinstance(it, GeneratorType)


def is_lambda(f):
    """
    Checks if function `f` is a lambda expression.
    
    Args:
        f (Callable[..., B]): the function to check

    Returns:
        bool: True if `f` is a lambda expression, False otherwise
    """
    return isinstance(f, LambdaType)


def is_thunk(f):
    """
    Checks if function `f` is a thunk, that is a lambda expression of arity zero.

    Args:
        f (Callable[..., B]): the function to check

    Returns:
        bool: True if `f` is a thunk, False otherwise
    """
    return is_lambda(f) and arity(f) == 0
