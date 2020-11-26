#!/usr/bin/env python
import os
from setuptools import setup


data = {'': ["VERSION.txt"]}
for folder in ["banners", "commands", "modules"]:
    for root, _, files in os.walk(os.path.join("dronesploit", folder)):
        _, root = root.split(os.path.sep, 1)
        for f in files:
            data[''].append(os.path.join(root, f))

setup(package_data=data)

