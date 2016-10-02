#!/bin/bash

sphinx-apidoc -f -o source ../genmonads && make html
