from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="dalle_runtime",
    version="0.1.0",
    url="https://github.com/axsaucedo/dalle_runtime.git",
    author="axsaucedo",
    author_email="",
    description="Runtime for Dalle model",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "mlserver==1.1.0",
        "torch==1.12.0+cu116",
        "flax",
        "jax==0.3.14",
        "jaxlib==0.3.14+cuda11.cudnn82",
    ],
    long_description=Path("README.md").read_text(),
    license="MIT",
)

