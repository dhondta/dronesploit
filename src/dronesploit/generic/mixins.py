# -*- coding: UTF-8 -*-
from .decorators import *


__all__ = ["FTPMixin", "TelnetMixin"]


class FTPMixin(object):
    """ Mixin class for adding a .send_ftp_command() method. """
    @ftp()
    def send_ftp_commands(self, *commands, username="root", password="*"):
        for c in commands:
            if __command(self._ftp, c, "sendcmd") is False:
                self.logger.error("There was an error with command %s" % str(command))
                return False
        return True


class RTSPMixin(object):
    """ Mixin class for adding . """


class TelnetMixin(object):
    """ Mixin class for adding a .send_telnet_command() method. """
    @telnet()
    def send_telnet_command(self, *commands, username="root", password="", prompt=b"~ # "):
        for c in commands:
            if __command(self._ftp, c, "write", True) is False:
                self.logger.error("There was an error with command %s" % str(command))
                return False
        return True

