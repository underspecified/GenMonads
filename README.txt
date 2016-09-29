# GenMonads: Python monads with generator-based do syntax
Author: Eric Nichols <underspecified@gmail.com>

This module contains python implementations of common scala-style monads.
It provides a generator-based do syntax using a decompilation trick from Pony [1]
to translate generators into nested calls to a monad's flat_map, map, and filter functions,
in a similar fashion to scala [2]. The idea was inspired by a comment by Shin no Noir [3]
on a post on A Neighborhood of Infinity [4].

## Requirements
* Python 3: https://www.python.org
* pony: https://pypi.python.org/pypi/pony

## Usage
>>> from genmonads.Option import *
>>> print(do(x + y
             for x in option(2)
             if x < 10
             for y in option(5)
             if y % 2 != 0))
Some(7)
>>> def make_gen():
        for x in option(4):
            if x > 2:
                for y in option(10):
                    if y % 2 == 0:
                        yield x - y
>>> print(do(make_gen()))
Some(-6)
>>> print(option(5) >> (lambda x: option(x * 2)))
Some(10)
>>> print(option(None))
None_()

## Todo
* variable assignment in generator functions
* Either[A,B] and other monads
* optional Haskell nomenclature?

## References
[1] http://stackoverflow.com/questions/16115713/how-pony-orm-does-its-tricks
[2] http://docs.scala-lang.org/tutorials/FAQ/yield.html
[3] https://www.blogger.com/profile/08974372500960094990
[4] http://blog.sigfpe.com/2012/03/overloading-python-list-comprehension.html
