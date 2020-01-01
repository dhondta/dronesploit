#!/usr/bin/env python
import os
import re
import dronesploit
from setuptools import setup, find_packages


with open("README.md", 'r') as f:
    long_descr = f.read()
with open("LICENSE", 'r') as f:
    license = f.read()


datafiles = [("", ["LICENSE"])]
for folder in ["banners", "commands", "modules"]:
    src = os.path.join("dronesploit", folder)
    datafiles += [(d, [os.path.join(d, f) for f in files])
                  for d, folders, files in os.walk(src)]

setup(
    version=dronesploit.__version__,
    packages=find_packages(),
    scripts=["bin/dronesploit"],
    install_requires=["sploitkit", "tinyscript", "pygments>=2.5.2"],
    python_requires=">=3.6, <4",
    setup_requires=["setuptools"],
    data_files=datafiles,
)
