# -*- coding: UTF-8 -*-
from sploitkit import *

from lib.wifi import *


class Scan(Command, ScanMixin):
    """ Scan for targets """
    def complete_keys(self):
        self.console.root.interfaces  # this triggers a refresh for INTERFACES
        return [i for i, mon in self.console.state['INTERFACES'].items() if mon]
    
    def run(self, interface, timeout=300):
        ScanMixin.run(self, interface, timeout)
    
    def validate(self, interface, timeout=300):
        if interface not in self.console.root.interfaces:
            raise ValueError("Bad wireless interface")
        if not self.console.state['INTERFACES'][interface]:
            raise ValueError("Wireless interface not in monitor mode")
        if int(timeout) <= 0:
            raise ValueError("Must be greater than 0")


class Targets(Command):
    """ Display the list of currently known targets """
    def run(self):
        data = [["ESSID", "BSSID", "Channel", "Power", "Enc", "Cipher", "Auth",
                 "Password"]]
        for target in self.console.state['TARGETS'].items():
            row = []
            for h in data[0]:
                row.append(target[h.lower()])
            data.append(row)
        if len(data) > 1:
            t = BorderlessTable(data, "Available Targets")
            print_formatted_text(t.table)
        else:
            self.logger.warning("No target available yet")


class Toggle(Command):
    """ Toggle monitor/managed mode for the given wireless interface """
    requirements = {'system': ["aircrack-ng/airmon-ng", "rfkill"]}
    
    def complete_values(self):
        return self.console.root.interfaces
    
    def run(self, interface):
        i = interface
        if self.console.state['INTERFACES'][i]:
            # turn off monitor mode
            self.console._jobs.run("sudo airmon-ng stop {}".format(i))
            self.logger.info("{} set back to managed mode".format(i))
        else:
            before = set(self.console.root.interfaces)
            # turn off the targeted interface
            self.console._jobs.run("sudo airmon-ng stop {}".format(i))
            # kill processes using this interface
            self.console._jobs.run("sudo airmon-ng check kill")
            # turn on monitor mode ; this will rename the interface
            out, err = self.console._jobs.run("sudo airmon-ng start {}"
                                              .format(i), stdin="y\n")
            new, name = None, None
            for line in out.split("\n"):
                if "monitor mode" in line:
                    _ = re.search(r"\[([a-z]+\d+)\](\w+)", line)
                    if _ is not None:
                        name, new = _.group(1), _.group(2)
                    break
            if new is None:
                self.logger.error("Could not set {} to monitor mode".format(i))
                return
            after = set(self.console.root.interfaces)
            new = list(after - before)[0]
            self.logger.info("{} set to monitor mode on {}".format(i, new))
            # ensure the interface is not soft-blocked
            out, _ = self.console._jobs.run("sudo rfkill list")
            for line in out.splitlines():
                parts = line.split(":", 2)
                if parts[1].strip() == name:
                    self.console._jobs.run("sudo rfkill unblock %s" % parts[0])
        self.console.root.interfaces  # this refreshes the state with INTERFACES
    
    def validate(self, interface):
        if interface not in self.console.root.interfaces:
            raise ValueError("Bad wireless interface")
