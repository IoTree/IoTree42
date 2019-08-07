## Adafruit Feather m0 Wi-Fi with tsl2591
### this code will do:

1. connect to Wi-Fi router
2. collect measurements (how many can be defined)
- each measurement contain: lux with timestamp provided by npc server
3. sends the measurements as json string to the Gateway

if the feather is plug to power chare.

 -> Measurement will stop and send.
if the feather is unplugged form power.

 -> measurement will begin

please define all necessary parameter in the script such as:
- Wi-Fi
- Gateway IP
