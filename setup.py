#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="brauna-financas",
    version="1.0.0",
    description="Aplicativo de gerenciamento financeiro pessoal",
    author="Brauna Finanças",
    author_email="contato@braunafinancas.com",
    url="https://github.com/braunafinancas/brauna-financas",
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.30.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.18.0",
        "matplotlib>=3.7.0",
        "pyyaml>=6.0",
        "pydantic>=2.4.0",
        "pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "brauna-financas=app.main:main",
        ],
    },
    package_data={
        "app": ["static/*", "data/sample/*"],
    },
) 