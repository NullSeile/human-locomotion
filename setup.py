"""
SETUP for Human-Locomotion (hl) package

You can either install this package static (changes in source will not affect
the installed package):
    $ pip install .

Or install with a symlink, so changes to the source files will be immediately
available to other users of the package on our system:
    $ pip install -e .
"""

from setuptools import find_packages, setup

DESCRIPTION = """Human-Locomotion package for training genetically a bipedal robot."""

setup(
    name="hl",
    version="0.0.0a",
    description=DESCRIPTION,
    url="https://github.com/NullSeile/human-locomotion.git",
    author="Daniel Azemar, Elies Bertran, Sam Farre, Monica Riu",
    install_requires=[
        "box2d-py",
        "tqdm",
        "pygame",
        "numpy",
        "pandas",
        "matplotlib",
    ],
    license="LICENCE.txt",
    packages=find_packages(exclude=("tests", "docs", "bin", "assests")),
    test_suite="tests",
    entry_points={
        "console_scripts": [],
    },
    scripts=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
