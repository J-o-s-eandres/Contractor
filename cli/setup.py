from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent

_readme = ""
for p in [HERE / "README.md", HERE.parent / "README.md"]:
    if p.exists():
        _readme = p.read_text(encoding="utf-8")
        break

setup(
    name="contractor-cli",
    version="0.1.0",
    description="Detect breaking changes in your OpenAPI specs before they hit production",
    long_description=_readme,
    long_description_content_type="text/markdown",
    url="https://github.com/J-o-s-eandres/Contractor",
    author="Joseandres",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
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
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
