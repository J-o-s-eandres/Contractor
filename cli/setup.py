from pathlib import Path

from setuptools import find_packages, setup

HERE = Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="contractor",
    version="0.1.0",
    description="Detect breaking changes in your OpenAPI specs before they hit production",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/J-o-s-eandres/Contractor",
    author="Joseandres",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
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
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
)
