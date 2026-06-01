from setuptools import setup, find_packages

setup(
    name="contractor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1",
        "rich>=13",
        "PyYAML>=6",
    ],
    entry_points={
        "console_scripts": [
            "contractor=contractor.cli:cli",
        ],
    },
    python_requires=">=3.11",
)
