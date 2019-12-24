#!/usr/bin/env python
import os
import re
from setuptools import setup, find_packages


with open("README.md", 'r') as f:
    long_descr = f.read()
with open("LICENSE", 'r') as f:
    license = f.read()
with open("requirements.txt", 'r') as f:
    reqs = [r.strip() for r in f.readlines() if r.strip() != ""]
with open("src/VERSION.txt", 'r') as f:
    version = f.read().strip()


os.rename("src", "dronesploit")
datafiles = []
for folder in ["banners", "commands", "modules"]:
    src = os.path.join("dronesploit", folder)
    datafiles += [(d, [os.path.join(d, f) for f in files])
                  for d, folders, files in os.walk(src)]

setup(
    name="dronesploit",
    version=version,
    packages=find_packages(),
    scripts=["bin/dronesploit"],
    install_requires=reqs,
    python_requires=">=3.6, <4",
    setup_requires=["setuptools"],
    data_files=datafiles,
    author="Alexandre D'Hondt",
    author_email="alexandre.dhondt@gmail.com",
    description="Drone pentesting framework console",
    long_description=long_descr,
    long_description_content_type="text/markdown",
    license=license,
    keywords="drone pentesting framework",
    url="https://github.com/dhondta/dronesploit",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
os.rename("dronesploit", "src")
