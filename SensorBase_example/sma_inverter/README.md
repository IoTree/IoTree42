## sma_inverter example
### RPI 2 - 4 /zero
#### this code will do:
1. connect to a sma inverter over modbus-tcp
2. get current active power and the Power over the day
3. sends velues to the server where it can be displayd in grafana e.g

Install python Module "socket", "paho.mqtt", "pymodbus" and "json".
This script is ment to be run on the gateway it self, but you can change it.

please define all necessary parameter in the script such as:
- sma_inverter_ip
- sma_inverter_port if needed
- and change hostname if script is not run on gateway it self.

####for more informations have a look at:
- for testing connection to sma_inverter follow this tutorial:
https://www.sma-sunny.com/en/how-to-test-the-connection-to-your-sma-inverter/

- Manual for sma inverter with deffinition of modbus tcp protocoll
https://files.sma.de/dl/24399/EDMM-10-Modbus-TI-de-13.pdf

- Modbus tcp client doc for python
pymodbus.readthedocs.io/en/latest/readme.html

