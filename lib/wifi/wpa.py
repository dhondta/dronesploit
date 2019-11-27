# -*- coding: UTF-8 -*-
import re


__all__ = ["WPAConnectMixin"]


REGEX = re.compile(r"(?m)Device '(?P<iface>[a-z][a-z0-9]*)' successfully "
                   r"activated with '(?P<uid>[0-9a-f\-]+)'\.")


class WPAConnectMixin(object):
    """ Mixin class for use with Command and Module """
    def run(self, essid):
        password = self.console.state['TARGETS'][essid]['password']
        out = self.console._jobs.run(["nmcli", "device", "wifi", "connect",
                                      essid, "password", password])[0]
        self.logger.debug(out)
        m = REGEX.search(out)
        if m is not None:
            self.console._jobs.run(["dhclient", m.group("iface")])
            return True
        return False
