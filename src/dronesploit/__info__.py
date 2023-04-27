# -*- coding: UTF-8 -*-
"""Dronesploit package information.

"""
import os

__author__    = "Alexandre D'Hondt"
__email__     = "alexandre.dhondt@gmail.com"
__copyright__ = ("A. D'Hondt", 2019)
__license__   = "agpl-3.0"

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as f:
    __version__ = f.read().strip()

