from itertools import zip_longest

__all__ = ['Wildcard', 'is_wildcard', 'match', 'matches', '_']


class Wildcard:
    pass
_ = Wildcard()


def is_wildcard(y):
    return type(y) == Wildcard


exhausted = ValueError('This iterable has been exhausted.')


def matches(a1, a2):
    """
    Checks if `a1` matches `a2`, taking into account wildcards in both type classes and arguments.

    Args:
        a1: the first type class to match
        a2: the second type class to match

    Returns:
        bool: True if `self` matches `other`, False otherwise
    """

    def _matches(l, r):
        return is_wildcard(l) or l == r

    def _matches_all(l, r):
        return all(_matches(l1, r1) for l1, r1 in zip_longest(l.unpack(), r.unpack(), fillvalue=exhausted))

    return type(a1) == type(a2) and a1.is_gettable() and a2.is_gettable() and _matches_all(a1, a2)


# noinspection PyProtectedMember
def match(x, conditions):
    """
    Checks a `Gettable[A]` type class instance `x` against dictionary of pattern => action mappings, and when a match
    is found, returns the results from calling the associated action on `x`'s inner value. Wildcard matches (`_`) are
    supported in both the type class and inner values.
    
    >>> from genmonads.match import match, _
    >>> from genmonads.option import Some, Nothing, option
    >>> x = option(5)
    >>> match(x, {
    >>>     Some(5-1):
    >>>         lambda y: print("Some(5-1) matches %s: %s" % (x, y)),
    >>>     Some(_):
    >>>         lambda y: print("Some(_) matches %s: %s" % (x, y)),
    >>>     Nothing():
    >>>         lambda: print("Nothing() matches:", x),
    >>>     _:
    >>>         lambda: print("Fallthrough wildcard matches:", x),
    >>> })
    Some(_) matches Some(5): 5

    Args:
        x (Gettable[A]): the type class to match against
        conditions (Dict[Gettable[A],Callable[[A],B]): a dictionary of pattern => action mappings

    Returns:
        Union[B,None]: the result of calling the matched action on `x`'s inner value or `None` if no match is found
    """
    for pattern, action in conditions.items():
        if is_wildcard(pattern):
            return action()
        elif matches(pattern, x):
            return action(*x.unpack())


def main():
    from genmonads.option import Some, Nothing, option
    x = option(5)
    x.match({
        Some(5-1):
            lambda y: print("Some(5-1) matches %s: %s" % (x, y)),
        Some(_):
            lambda y: print("Some(_) matches %s: %s" % (x, y)),
        Nothing():
            lambda: print("Nothing() matches", x),
        _:
            lambda: print("Fallthrough wildcard matches:", x),
    })

if __name__ == '__main__':
    main()
