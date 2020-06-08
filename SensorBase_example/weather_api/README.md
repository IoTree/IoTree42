## weather example
### RPI 2 - 4 /zero
#### this code will do:
1. connect openweather.org
2. get json form api
3. sends velues to the server where it can be displayd in grafana e.g

Install python Module "requests". "paho.mqtt" and "json".
This script is ment to be run on the gateway it self, but you can change it.

!!!You will need an account on openweather.org to get an api_key!!!

please define all necessary parameter in the script such as:
- api_key
- city
- country
