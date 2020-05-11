# -*- coding: UTF-8 -*-
__copyright__ = "E. Borel"
__license__ = "agpl-3.0"
__doc__ = """
Module for sniffing NincoAir ID's
"""
from sploitkit import *

from lib.radio.SDRModule import SnifferModule, SDRModule
import time

from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
import osmosdr

class SniffNinco(SnifferModule):
	"""
	Utility scanning IDs of NincoAir.
	The frequency chosen by the drone can be between qround 2.402e9 and 2.483e9, so we arbitrary chose 2.405, because an authentication request will be normally sent on this frequency
	The meta-parameter FREQUENCY is then ignored
	"""

	def run(self):
		"""
		Parameter FREQUENCY ignored
		"""
		self.init()
		try:
			osmosdr_source = osmosdr.source( args="numchan=" + str(1) + " " + self.config.option(SDRModule.SDR_ARGS).value)
		except:
			return
		osmosdr_source.set_sample_rate(self.samp_rate)
		osmosdr_source.set_center_freq(2.408e9, 0)
		osmosdr_source.set_freq_corr(0, 0)
		osmosdr_source.set_dc_offset_mode(0, 0)
		osmosdr_source.set_iq_balance_mode(0, 0)
		osmosdr_source.set_gain_mode(False, 0)
		osmosdr_source.set_gain(10, 0)
		osmosdr_source.set_if_gain(20, 0)
		osmosdr_source.set_bb_gain(20, 0)
		osmosdr_source.set_antenna('', 0)
		osmosdr_source.set_bandwidth(0, 0)
		container = gr.top_block()
		digital_gmsk_demod_0 = digital.gmsk_demod(samples_per_symbol=self.samp_syms,gain_mu=0.175,mu=0.5,omega_relative_limit=0.005,freq_error=0.0,verbose=False,log=False,)
		digital_correlate_access_code_xx_ts_0 = digital.correlate_access_code_bb_ts(bin(0xaaaaa)[2:], 4, 'ninco')
		blocks_vector_sink_x_0 = blocks.vector_sink_b(1)
		blocks_repack_bits_bb_0 = blocks.repack_bits_bb(1, 8, "", False, gr.GR_MSB_FIRST)
		container.connect((blocks_repack_bits_bb_0, 0), (blocks_vector_sink_x_0, 0))
		container.connect((digital_correlate_access_code_xx_ts_0, 0), (blocks_repack_bits_bb_0, 0))
		container.connect((digital_gmsk_demod_0, 0), (digital_correlate_access_code_xx_ts_0, 0))
		container.connect((osmosdr_source, 0), (digital_gmsk_demod_0, 0))
		container.start()
		time.sleep(self.timeout)
		data = list(blocks_vector_sink_x_0.data())
		indexes = self.find_sub_list([0xaa, 0xaa], data)
		if len(indexes) > 0:
			self.logger.success("Possible captured IDs")
			for idx in indexes:
				mark = idx[0]
				self.logger.success(", ".join(hex(x)[2:].zfill(2) for x in data[mark:mark + 10]))
				break
		else:
			self.logger.warning("No IDs found. ")
		container.stop()
		container.wait()
		osmosdr_source.disconnect_all()
