#!/bin/bash

sphinx-apidoc -f -o source ../genmonads && \
#pandoc --from=markdown --to=rst --output=README.rst README.md 
make html
