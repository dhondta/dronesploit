# -*- coding: UTF-8 -*-
__copyright__ = "E. Borel"
__license__ = "agpl-3.0"
__doc__ = """
Module for NincoQir Quadrone mini
"""

from sploitkit import *
from .SDRModule import SDRModule

from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
import osmosdr

class NincoAirModule(SDRModule):
        """
        :This drone uses a channel between 2.402 GHz and 2.483 GHz, separated by 0.003 GHz. Some channels or ore often used, but it is recommended to look for the alocated channel with tools such as GQRX, and then launch the exploits. Another interesting fact is that packets are normally ended by a 24-bits CRC, but packets without CRC are accepted
        """

        def __init__(self):
                super(NincoAirModule, self).__init__()
                self.preamble = [255, 255, 255, 255, 255, 170, 170, 170]
                self.TXid = [145, 68, 45, 45, 0, 224, 83]

        def run(self, vector):
                """
                Generic run method modulating a vector and transmitting it like [vector|short silence|vector] repeatedly
                """
                self.init()
                if self.osmosdr_sink == None:
                        return
                container = gr.top_block()
                digital_gmsk_mod_0_0 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
                digital_gmsk_mod_0 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
                blocks_vector_source_x_1_1 = blocks.vector_source_b(vector, True, 1, [])
                blocks_vector_source_x_1_0 = blocks.vector_source_c((self.silent,), True, 1, [])
                blocks_vector_source_x_1 = blocks.vector_source_b(vector, True, 1, [])
                blocks_stream_mux_0 = blocks.stream_mux(gr.sizeof_gr_complex*1, (len(vector) * 8 * self.samp_syms, 2500, len(vector) * 8 * self.samp_syms))
                container.connect((blocks_stream_mux_0, 0), (self.osmosdr_sink, 0))
                container.connect((blocks_vector_source_x_1, 0), (digital_gmsk_mod_0, 0))
                container.connect((blocks_vector_source_x_1_0, 0), (blocks_stream_mux_0, 1))
                container.connect((blocks_vector_source_x_1_1, 0), (digital_gmsk_mod_0_0, 0))
                container.connect((digital_gmsk_mod_0, 0), (blocks_stream_mux_0, 0))
                container.connect((digital_gmsk_mod_0_0, 0), (blocks_stream_mux_0, 2))
                container.start()
                self.wait_for_exit()
                container.stop()
                container.wait()
                self.osmosdr_sink.disconnect_all()

