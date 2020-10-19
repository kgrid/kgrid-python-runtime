import setuptools
from setuptools.command.install import install
import os

with open("README.md", "r") as fh:
    long_description = fh.read()


class CustomInstallCommand(install):
    def run(self):
        if not os.path.exists('pyshelf'):
            print('Creating shelf directory')
            os.mkdir('pyshelf')
        install.run(self)


setuptools.setup(
    cmdclass={'install': CustomInstallCommand},
    name="kgrid-python-runtime",
    version="0.0.6",
    author="Kgrid Developers",
    author_email="kgrid-developers@umich.edu",
    description="A runtime for python-based Knowledge Objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kgrid/kgrid-python-runtime",
    packages=[
        'kgrid_python_runtime'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    python_requires='>=3.8',
    install_requires=['flask', 'Flask-Script', 'werkzeug', 'requests', 'responses']
)
