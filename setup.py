from setuptools import setup, find_packages
from zero.version import __version__ as version
import os

readme_file = os.path.join(os.path.dirname(__file__), "README.md")

with open(readme_file, "r") as fh:
    long_description = fh.read()

setup(
    name="nyun",
    version=version,
    author="NyunAI",
    author_email="contact@nyunai.com",
    description="A CLI package with 'init' and 'run' commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nyunai/zero",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "typer",
        "docker",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "nyun=zero.cli:app",
        ],
    },
    extras_require={

    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)