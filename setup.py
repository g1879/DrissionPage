# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="DrissionPage",
    version="2.0.3",
    author="g1879",
    author_email="g1879@qq.com",
    description="A module that integrates selenium and requests session, encapsulates common page operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    keywords="DrissionPage",
    url="https://gitee.com/g1879/DrissionPage",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "selenium",
        "lxml",
        "tldextract",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.6'
)
