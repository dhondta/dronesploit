#!/usr/bin/env python
import os
import re
import dronesploit
from setuptools import setup, find_packages


datafiles = [("", ["LICENSE"])]
for folder in ["banners", "commands", "modules"]:
    src = os.path.join("dronesploit", folder)
    datafiles += [(d, [os.path.join(d, f) for f in files])
                  for d, folders, files in os.walk(src)]

setup(data_files=datafiles)
