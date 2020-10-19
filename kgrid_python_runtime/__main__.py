import os
from kgrid_python_runtime.app import runserver

if not os.path.exists('pyshelf'):
    os.makedirs('pyshelf')

runserver()

