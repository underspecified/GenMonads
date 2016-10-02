# GenMonads: Python monads with generator-based syntax
Author: Eric Nichols <underspecified@gmail.com>

This module contains python implementations of some scala-style monads.

It provides a generator-based syntax using a decompilation trick from Pony [1]
to translate generators into nested calls to a monad's flat_map, map, and
filter functions, in a similar fashion to scala's for comprehensions [2].

The idea was inspired by a comment by Shin no Noir [3] on a post on A
Neighborhood of Infinity [4].


## Features

GenMonads supports do-notation-like syntax by using a special function to
evaluate a generator over monads (the functions is named "mfor," short for
"monadic for comprehension," as it is modeled after scala's for comprehensions,
but the synonym "do" is also available):

```python
>>> from genmonads.Option import *
>>> print(mfor(x + y
               for x in option(2)
               if x < 10
               for y in option(5)
               if y % 2 != 0))
Some(7)
```

The above generator is automatically translated into the following at run-time:

```python
>>> print(option(2) \
              .filter(lambda x: x < 10) \
              .flat_map(lambda x: option(5) \
                   .filter(lambda y: y % 2 != 0) \
                   .map(lambda y: x + y)))
Some(7)
```

Both generator expressions and generator functions are supported, though
variable assignment in generator function bodies is not currently implemented:

```python
>>> def make_gen():
        for x in option(4):
            if x > 2:
                for y in option(10):
                    if y % 2 == 0:
                        yield x - y
>>> print(mfor(make_gen()))
Some(-6)
```

Monad chaining with the bind operator is also supported (>>= and >> are
combined into a single >> operator due to syntactic limitations in
overloading >>= in python):

```python
>>> print(option(5) >> (lambda x: option(x * 2)))
Some(10)
>>> print(option(5) >> (lambda _: option(2)))
Some(2)
```
Following scala's monadic handling of nulls, the option(...) function can be
used to inject computations that can return None into the Option monad:

```python
>>> print(option(None))
Nothing()
>>> pets = {'cat': 1, 'dog': 2, 'bird': 3}
>>> print(option(pets.get('dog')))
Some(2)
>>> print(option(pets.get('iguana')))
Nothing()
```

## Requirements
* Python 3: https://www.python.org
* pony: https://pypi.python.org/pypi/pony


## Todo
* variable assignment in generator functions
* optional Haskell nomenclature
* Either[A,B] and other monads
* Try.or_else(recover)


## License
This project is licensed under the GNU Affero General Public License v3 (AGPLv3).


## References
[1] http://stackoverflow.com/questions/16115713/how-pony-orm-does-its-tricks
[2] http://docs.scala-lang.org/tutorials/FAQ/yield.html
[3] https://www.blogger.com/profile/08974372500960094990
[4] http://blog.sigfpe.com/2012/03/overloading-python-list-comprehension.html
