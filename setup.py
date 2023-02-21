from pathlib import Path
from setuptools import find_packages, setup
from needle import __version__


setup(
    name="needle",
    version=__version__,
    author="devforfu",
    author_email="developer.z@outlook.com",
    description="A package helping to navigate nested structures easily",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/devforfu/needle",
    packages=find_packages(),
    classifiers=["Programming Langauge :: Python :: 3"],
    python_requires=">=3.9",
)

