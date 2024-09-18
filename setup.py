# -*- coding:utf-8 -*-
from setuptools import setup, find_packages
from DrissionPage import __version__

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="DrissionPage",
    version=__version__,
    author="g1879",
    author_email="g1879@qq.com",
    description="Python based web automation tool. It can control the browser and send and receive data packets.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    keywords="DrissionPage",
    url="https://DrissionPage.cn",
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        'lxml',
        'requests',
        'cssselect',
        'DownloadKit>=2.0.2',
        'websocket-client',
        'click',
        'tldextract',
        'psutil'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'dp = DrissionPage._functions.cli:main',
        ],
    },
)
