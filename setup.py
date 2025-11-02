#!/usr/bin/env python3
"""
Setup script for qBittorrent Remote Client
"""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="qbittorrent-remote-client",
    version="0.0.1",
    author="rlong",
    description="A Python-based command-line tool for remotely managing qBittorrent instances via the Web API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rlong/qbittorrent-remote-client",
    py_modules=["qbt_api", "qbt_client"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications :: File Sharing",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "qbt-client=qbt_client:main",
        ],
    },
)
