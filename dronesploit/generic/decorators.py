# -*- coding: UTF-8 -*-
from ftplib import FTP
from telnetlib import Telnet
from tinyscript import b
from tinyscript.helpers import is_function, is_list


__all__ = ["anonymous_ftp", "ftp", "telnet"]


def __command(client, command, default_method, use_bytes=False):
    """ Private function supporting multiple command formats:
        - string
        - function
        - (function, args, kwargs) """
    if is_function(command):
        return command(client)
    elif is_list(command):
        a, kw = (), {}
        try:
            command, a, kw = command
        except ValueError:
            pass
        try:
            command, a = command
        except ValueError:
            pass
        return command(client, *a, **kw)
    else:
        return getattr(client, default_method)(b(command) if use_bytes else command)


def anonymous_ftp(*commands):
    """ Shortcut decorator for binding a temporary FTP client with an anonymous session. """
    return ftp(*commands, username="anonymous", password="anonymous")


def ftp(*commands, **params):
    """ Decorator for binding a temporary FTP client. """
    def _wrapper(f):
        def _subwrapper(self, *args, **kwargs):
            self.logger.info("Starting an FTP session...")
            f = self._ftp = FTP(self.config.option("IP").value, self.config.option("FTP_PORT").value)
            username = kwargs.pop('username', params.get('username', self.config.option("FTP_USERNAME").value))
            if username:
                self.logger.debug("Authenticating...")
                f.sendcmd("USER %s" % username)
                password = kwargs.pop('password', params.get('password', self.config.option("FTP_PASSWORD").value))
                f.sendcmd("PASS %s" % password)
            for c in commands:
                if __command(self._ftp, c, "sendcmd") is False:
                    self.logger.error("There was an error with command %s" % str(command))
                    r = False
                    break
            try:
                r
            except NameError:
                r = f(self, *args, **kwargs)
            self._ftp.quit()
            delattr(self, "_ftp")
            return r
        return _subwrapper
    return _wrapper


def telnet(*commands, **params):
    """ Decorator for binding a temporary Telnet client. """
    def _wrapper(f):
        def _subwrapper(self, *args, **kwargs):
            self.logger.debug("Starting a Telnet session...")
            t = self._telnet = Telnet(self.config.option("IP").value)
            # Telnet authentication preamble
            username = kwargs.pop('username', params.get('username', self.config.option("TELNET_USERNAME").value))
            if username:
                self.logger.debug("[DRO] " + t.read_until(b"login: ").decode("utf-8"))
                self.logger.debug("[ATT] " + username)
                t.write(b"%s\n" % b(username))
                self.logger.debug("[DRO] " + t.read_until(b"assword: ").decode("utf-8"))
                pswd = self.config.option("PASSWORD").value
                self.logger.debug("[CLI] " + pswd)
                t.write(b"%s\n" % b(kwargs.pop('password', params.get('password',
                                                          self.config.option("TELNET_PASSWORD").value))))
            resp = t.read_until(b(kwargs.pop('prompt', params.get('prompt', "~ # "))))
            self.logger.debug("[DRO] " + resp.decode("utf-8"))
            if not b(kwargs.pop('preamble', params.get('preamble', ""))) in resp:
                self.logger.error("Authentication failed")
                return False
            for c in commands:
                if __command(self._ftp, c, "write", True) is False:
                    self.logger.error("There was an error with command %s" % str(command))
                    r = False
                    break
            try:
                r
            except NameError:
                r = f(self, *args, **kwargs)
            self.logger.debug("[CLI] exit")
            t.write(b"exit\n")
            t.read_all()
            t.close()
            delattr(self, "_telnet")
            return r
        return _subwrapper
    return _wrapper

