# -*- coding: UTF-8 -*-
"""Dronesploit package information.

"""
import os

__author__    = "Alexandre D'Hondt"
__email__     = "alexandre.dhondt@gmail.com"
__copyright__ = "© 2019-2020 A. D'Hondt"
__license__   = "agpl-3.0"

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as f:
    __version__ = f.read().strip()

