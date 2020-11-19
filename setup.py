import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

this_dir = os.path.dirname(os.path.realpath(__file__))
requirements = os.path.join(this_dir, 'requirements.txt')
install_requires = []
if os.path.isfile(requirements):
    with open(requirements) as file:
        install_requires = file.read().splitlines()

with open(os.path.join(this_dir, 'kgrid_python_runtime', 'VERSION')) as version_file:
    version = version_file.read().strip()

setuptools.setup(
    name="kgrid-python-runtime",
    version=version,
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
    install_requires=install_requires,
    include_package_data=True
)
