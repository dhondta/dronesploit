#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tinyscript package information.

"""
import os

__author__    = "Alexandre D'Hondt"
__copyright__ = "© 2019-2020 A. D'Hondt"
__license__   = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"

with open(os.path.join(os.path.dirname(__file__), "VERSION.txt")) as f:
    __version__ = f.read().strip()
