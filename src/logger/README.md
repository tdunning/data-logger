# Data Logger

This data logger records data from a DS18B20 or similar device attached to a AdaFruit Huzzah or similar board.  Power consumption is kept very low by using the deep sleep capability of the board and multiple temperature sensors can be attached to a single controller. Battery based operation for many months should be possible.


## Software Design

The WIFI parameters are configured into the board once using the REPL interface. The following lines should work:

```
import wlan
wlan = network.WLAN(network.STA_IF) # create station interface
wlan.active(True)       # activate the interface
wlan.connect('te-home2', '769AC43D9F') # connect to an AP
```

Beyond this, each time the board is reset, it will scan through all of the temperature sensors that it can find and report a value for each of them. At that point, it will schedule a wakeup

Data is reported back to a central server using a custom data log server. Each measured data point is sent using a URL of the form:

`http://<server>/data/<board>/<sensor>/<value>`

Here `server` is the name of the central server, `board` is the unique identifier of the controller that is reporting the data, sensor is a unique ID for each sensor and `value` is the measured value.

Each time the board wakes up, it will download a configuration file from the server that includes, possibly among other parameters, the time the controller should sleep before next waking. The configuration file is in JSON format and is accessible from the following URL

`http://<server>/config/<board>`

The final action of the control is to schedule a wakeup and enter deep sleep. If directed in the config file, it will not actually sleep, but will start a web REPL and wait for instructions. Starting a REPL allows debugging of the controller software by going to `http://<ip>:8266/` where `ip` is the IP address of the board which can be found in the server logs.

## Hardware Design

To support the wake function, pin D0 (GPIO16) should be connected to the RST pin using a 400 ohm resistor. This allows the real-time to wake the board, but also allows the reset button to be used to wake the board (and thus force a measurement).

Temperature sensors should have their data lines connected to pin D6 (GPIO12) and be powered from the nearby 3V3 and GND lines. It is not clear whether a 4.7k ohm pullup is required on the data line, but the initial test board did not require this for a single temperature sensor. Multiple sensors can be connected to the same lines and each will report with a distinct ID.

In the future, it would be nice to allow the board to monitor and report its own battery level.

## Security Roadmap

Currently, all data is reported using HTTP (without TLS) and there is no attempt to avoid spoofing. This is fine for now. If it becomes desirable to prevent spoofing, the plan is to have a registration URL

`http://<server>/register/<board>`

If this particular board has never registered before, then the server will return a key that can be used to authenticate further transactions. This key should be saved by the controller in non-volatile memory. Each time data is reported, the transaction will include a header row with a monotonically increasing transaction number and a header with the hash of the URL used to report the data (including value) and the transaction number.

