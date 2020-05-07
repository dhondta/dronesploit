# -*- coding: UTF-8 -*-
__copyright__ = "E. Borel"
__license__ = "agpl-3.0"
__doc__ = """
Module for sniffing XN297 ID's
"""

from sploitkit import *

from lib.radio.SDRModule import SnifferModule, SDRModule
import time
from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
import osmosdr

class SniffXN297(SnifferModule):
	"""
	Utility scanning IDs of drones using XN297 chip.
	The ID might be from 3 to 5 bytes long
	"""

	def __init__(self):
		super(SniffXN297, self).__init__()

	def run(self):
		self.init()
		try:
			osmosdr_dev = osmosdr.source( args="numchan=" + str(1) + " " + self.config.option(SDRModule.SDR_ARGS).value )
		except:
			return
		osmosdr_dev.set_sample_rate(self.samp_rate)
		osmosdr_dev.set_center_freq(self.frequency, 0)
		osmosdr_dev.set_freq_corr(0, 0)
		osmosdr_dev.set_dc_offset_mode(0, 0)
		osmosdr_dev.set_iq_balance_mode(0, 0)
		osmosdr_dev.set_gain_mode(False, 0)
		osmosdr_dev.set_gain(self.rf_gain, 0)
		osmosdr_dev.set_if_gain(self.if_gain, 0)
		osmosdr_dev.set_bb_gain(self.bb_gain, 0)
		osmosdr_dev.set_antenna('', 0)
		osmosdr_dev.set_bandwidth(0, 0)
		container = gr.top_block()
		digital_gmsk_demod_0 = digital.gmsk_demod(samples_per_symbol=self.samp_syms,gain_mu=0.175,mu=0.5,omega_relative_limit=0.005,freq_error=0.0,verbose=False,log=False,)
		digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts(bin(0x710f55)[2:], 4, 'xn297')
		vector_sink = blocks.vector_sink_b(1)
		blocks_repack_bits_bb_0 = blocks.repack_bits_bb(1, 8, "", False, gr.GR_MSB_FIRST)
		container.connect((blocks_repack_bits_bb_0, 0), (vector_sink, 0))
		container.connect((digital_correlate_access_code_xx_ts_0, 0), (blocks_repack_bits_bb_0, 0))
		container.connect((digital_gmsk_demod_0, 0), (digital_correlate_access_code_xx_ts_0, 0))
		container.connect((osmosdr_dev, 0), (digital_gmsk_demod_0, 0))
		self.logger.info("Starting capturing traffic on given frequency during %d seconds" % self.timeout)
		container.start()
		time.sleep(self.timeout)
		data = list(vector_sink.data())
		indexes = self.find_sub_list([0x71, 0x0F, 0x55], data)
		if len(indexes) == 0:
			self.logger.warning("Preamble 71 0F 55 not found. ")
		else:
			self.logger.success("Possible captured IDs (from 3 to 5 bytes):")
			for idx in indexes:
				mark = idx[1]
				self.logger.success(", ".join([hex(x)[2:].zfill(2) for x in data[mark+1:mark + 6]]))
		container.stop()
		container.wait()
		osmosdr_dev.disconnect_all()

