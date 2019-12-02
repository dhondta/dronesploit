# -*- coding: UTF-8 -*-
from prompt_toolkit.formatted_text import ANSI
from sploitkit import *
from termcolor import colored

from lib.wifi import *


class Connect(Command, WPAConnectMixin):
    """ Connect to an Access Point """
    def complete_values(self):
        targets = self.console.state['TARGETS']
        return [t for t, d in targets.items() if d.get('password') is not None]
    
    def run(self, essid):
        if WPAConnectMixin.run(self, essid):
            self.logger.success("Connected to {}".format(essid))
            for t, d in self.console.state['TARGETS'].items():
                d['connected'] = t == essid
        else:
            self.logger.failure("Connection to {} failed".format(essid))


class Password(Command):
    """ Manually set the password of an Access Point """
    def complete_keys(self):
        targets = self.console.state['TARGETS']
        return [t for t in targets.keys() if 'password' in targets[t]]
    
    def complete_values(self, target=None):
        targets = self.console.state['TARGETS']
        return [t['password'] for _, t in targets.items() if t['password']]
    
    def run(self, essid, password):
        self.console.state['TARGETS'][essid]['password'] = password
        self.logger.success("({}) password => {}".format(essid, password))
    
    def validate(self, essid, password):
        if essid not in self.complete_keys():
            raise ValueError("invalid target")


class Scan(Command, ScanMixin):
    """ Scan for targets """
    def __init__(self, *args, **kwargs):
        super(Scan, self).__init__(*args, **kwargs)
        self._filter_func = drone_filter
    
    def complete_keys(self):
        self.console.root.interfaces  # this triggers a refresh for INTERFACES
        return [i for i, mon in self.console.state['INTERFACES'].items() if mon]
    
    def run(self, interface, timeout=300):
        ScanMixin.run(self, interface, timeout)
    
    def validate(self, interface, timeout=300):
        if interface not in self.console.root.interfaces:
            raise ValueError("bad wireless interface")
        if not self.console.state['INTERFACES'][interface]:
            raise ValueError("wireless interface not in monitor mode")
        if int(timeout) <= 0:
            raise ValueError("must be greater than 0")


class Targets(Command):
    """ Display the list of currently known targets """
    def run(self):
        data = [["ESSID", "BSSID", "Channel", "Power", "Enc", "Cipher", "Auth",
                 "Password", "Stations"]]
        for _, target in self.console.state['TARGETS'].items():
            c = target['connected']
            rows = []
            for i, h in enumerate(data[0]):
                rows.append([""] * len(data[0]))
                v = target[h.lower()]
                if isinstance(v, (tuple, list)):
                    for j in range(len(v) - 1):
                        rows.append([""] * len(data[0]))
                else:
                    v = [v]
                for j, sv in enumerate(v):
                    if c:
                        sv = colored(sv, attrs=['bold'])
                    rows[j][i] = sv
            for r in rows:
                if all(v == "" for v in r):
                    continue
                data.append(r)
        if len(data) > 1:
            t = BorderlessTable(data, "Available Targets")
            print_formatted_text(ANSI(t.table))
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
                    m = re.search(r"\[([a-z]+\d+)\](\w+)", line)
                    if m is not None:
                        name, new = m.group(1), m.group(2)
                    break
            if new is None:
                self.logger.error("Could not set {} to monitor mode".format(i))
                return
            after = set(self.console.root.interfaces)
            new = list(after - before)[0]  #FIXME: empty list when problem with
                                           #        interface half-set
            self.logger.info("{} set to monitor mode on {}".format(i, new))
            # ensure the interface is not soft-blocked
            out, _ = self.console._jobs.run("sudo rfkill list")
            for line in out.splitlines():
                parts = line.split(":", 2)
                if parts[1].strip() == name:
                    self.console._jobs.run("sudo rfkill unblock %s" % parts[0])
        self.console.root.interfaces  # this refreshes the state with INTERFACES
        Entity.check()
    
    def validate(self, interface):
        if interface not in self.console.root.interfaces:
            raise ValueError("bad wireless interface")
