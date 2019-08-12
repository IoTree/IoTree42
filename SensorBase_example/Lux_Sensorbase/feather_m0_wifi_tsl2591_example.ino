
//Iotree42 sensor Netzwerk 

//purpors: logged sensor data send by mqtt over Wifi to Gateway 
//with software: timestemp, jsonlogging, mqtt
//with hardware: tsl2591 light sersor, Adafruit feather m0 wifi

//designt by Sebastin Stadler
//on behalf of the university of munich.

 
#include <SPI.h>
#include <WiFi101.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_TSL2591.h"
#include <ArduinoJson.h>
#include <TimeLib.h>
#include <WiFiUdp.h>

/*-------- dif. USB Power check ----------*/
int sensorPin = A5;   // select the input pin for powersurce check
int sensorValue = 0.0;  // variable to store the value coming from the pin A5

/*-------- dif. mesuerment loops  ----------*/
int m = 120;           //max loop depends on how big the json opject per mesuerment is look at github explanation
                      //Or how often you want to send data to the gateway. m set to = 1 -> every singl mesuerment is send
int mtime = 30000;    //Mesurement time in milisec

/*-------- dif. Wifi ----------*/
#include "arduino_secrets.h" 
//please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = "****";         // your network SSID (name)
char pass[] = "****";                // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;                           // your network key Index number (needed only for WEP)
int status = WL_IDLE_STATUS;
WiFiServer server(80);

/*-------- dif. Mqtt ----------*/
const char* mqttServer = "";   //set gateway IP here
const int mqttPort = 1883;                  //set gateway Port used by mosquitto broker here
WiFiClient espClient;
PubSubClient client(espClient);
char pubtopic = "sensorbase/feather08/tsl2591"

/*-------- dif. json ----------*/
char attributes[500];

/*-------- dif. tsl 2591 ----------*/
Adafruit_TSL2591 tsl = Adafruit_TSL2591(2591); // pass in a number for the sensor identifier (for your use later)
void configureSensor(void){
  // You can change the gain on the fly, to adapt to brighter/dimmer light situations
  tsl.setGain(TSL2591_GAIN_LOW);               // 1x gain (bright light)
  //tsl.setGain(TSL2591_GAIN_MED);             // 25x gain
  //tsl.setGain(TSL2591_GAIN_HIGH);            // 428x gain
  
  // Changing the integration time gives you a longer time over which to sense light
  // longer timelines are slower, but are good in very low light situtations!
  tsl.setTiming(TSL2591_INTEGRATIONTIME_100MS);     // shortest integration time (bright light)
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_200MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_300MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_400MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_500MS);
  // tsl.setTiming(TSL2591_INTEGRATIONTIME_600MS);  // longest integration time (dim light)
  /* Display the gain and integration time for reference sake */  
  Serial.println(F("------------------------------------"));
  Serial.print  (F("Gain:         "));
  tsl2591Gain_t gain = tsl.getGain();
  switch(gain){
    case TSL2591_GAIN_LOW:
      Serial.println(F("1x (Low)"));
      break;
    case TSL2591_GAIN_MED:
      Serial.println(F("25x (Medium)"));
      break;
    case TSL2591_GAIN_HIGH:
      Serial.println(F("428x (High)"));
      break;
    case TSL2591_GAIN_MAX:
      Serial.println(F("9876x (Max)"));
      break;}
  Serial.print  (F("Timing:       "));
  Serial.print((tsl.getTiming() + 1) * 100, DEC); 
  Serial.println(F(" ms"));
  Serial.println(F("------------------------------------"));
  Serial.println(F(""));}

/*-------- dif time udp ----------*/
// NTP Servers:
static const char ntpServerName[] = "us.pool.ntp.org";
const int timeZone = 0;     // UTC +-0
WiFiUDP Udp;
unsigned int localPort = 8888;  // local port to listen for UDP packets
time_t getNtpTime();
void digitalClockDisplay();
void printDigits(int digits);
void sendNTPpacket(IPAddress &address);
time_t prevDisplay = 0; // when the digital clock was displayed


/*-------- Starting setup ----------*/
void setup() {

  /*--------------Settings and connections------------------*/
  
  //Configure pins for Adafruit ATWINC1500 Feather
  WiFi.setPins(8,7,4,2);
  
  ////Initialize serial and wait for port to open:
  //Serial.begin(9600);
  //while (!Serial) {
  //  ; // wait for serial port to connect. Needed for native USB port only
  //}

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);
    // wait 1 seconds for connection:
    delay(2000);
  }
  server.begin();
  // you're connected now and use low power mode reduses wifi to ~12mA instad of 100mA
  WiFi.lowPowerMode();

  //setup tsl2591
  Serial.println(F("Starting Adafruit TSL2591 Test!"));
  if (tsl.begin()) 
  {
    Serial.println(F("Found a TSL2591 sensor"));
  } 
  else 
  {
    Serial.println(F("No sensor found ... check your wiring?"));
    while (1);
  } 
  /* Configure the sensor */
  configureSensor();

  //setup get time form server
  Udp.begin(localPort); //Starting udp
  //Serial.println(Udp.localPort());
  setSyncProvider(getNtpTime); //Where to get the time
  setSyncInterval(3600); //Time interval to next sync in sec
}


/*-------- Starting loop ----------*/
void loop() {
    // check if power is bluged in
    sensorValue = analogRead(sensorPin);
    sensorValue *= 2;
    sensorValue *= 3,3;
    if (sensorValue >= 5300){
      Serial.print("warte");
      delay(600000); // wait 10 min and than check again
    }
    else{
      //setup json array and doc
      StaticJsonDocument<20000> doc;
      JsonArray data = doc.createNestedArray("data");
      //starting mesurement Loop
      int var = 0; // Zähler für while
      while (var < m){
        // check if still no power pluged in
        sensorValue = analogRead(sensorPin);
        sensorValue *= 2;
        sensorValue *= 3,3;
        if (sensorValue >=5300 ){
          break;
        }
        var++;
        //collecting light data
        Serial.println("Collecting light data.");
        // Reading visble light 350 milliseconds!
        float lux = tsl.getLuminosity(TSL2591_VISIBLE);
        // Check if any reads failed and exit early (to try again).
        if (isnan(lux)) {
          Serial.println("Failed to read from TSL 2591 sensor!");
          return;
        }
        // Save to jsonfile
        JsonObject opj_var = data.createNestedObject();
        opj_var["lux"] = lux;  //lux value
        opj_var["time"] = now(); //unix time firm utp server
        delay(mtime); // meserment loop time
        }
      // connecting to mqtt Broker
      client.setServer(mqttServer, mqttPort);
      while(!client.connected()) {
        Serial.println("Connecting to MQTT...");
        if(client.connect("ESP8266Client")) {
          Serial.println("connected");
        }else{
          Serial.print("failed state ");
          Serial.print(client.state());
          delay(200);
        }
      }
      //sending Json data via Mqtt   
      for (int n =0; n <= var-1; n++){ //loop thrught json data end sending each
        serializeJson(data[n], attributes);
        client.publish( puptopic, attributes );
        Serial.println( attributes );
        client.loop();
      }
      delay(100);
      client.disconnect();
    }
  }


/*-------- NTP code ----------*/

const int NTP_PACKET_SIZE = 48; // NTP time is in the first 48 bytes of message
byte packetBuffer[NTP_PACKET_SIZE]; //buffer to hold incoming & outgoing packets

time_t getNtpTime()
{
  IPAddress ntpServerIP; // NTP server's ip address

  while (Udp.parsePacket() > 0) ; // discard any previously received packets
  Serial.println("Transmit NTP Request");
  // get a random server from the pool
  WiFi.hostByName(ntpServerName, ntpServerIP);
  Serial.print(ntpServerName);
  Serial.print(": ");
  Serial.println(ntpServerIP);
  sendNTPpacket(ntpServerIP);
  uint32_t beginWait = millis();
  while (millis() - beginWait < 1500) {
    int size = Udp.parsePacket();
    if (size >= NTP_PACKET_SIZE) {
      Serial.println("Receive NTP Response");
      Udp.read(packetBuffer, NTP_PACKET_SIZE);  // read packet into the buffer
      unsigned long secsSince1900;
      // convert four bytes starting at location 40 to a long integer
      secsSince1900 =  (unsigned long)packetBuffer[40] << 24;
      secsSince1900 |= (unsigned long)packetBuffer[41] << 16;
      secsSince1900 |= (unsigned long)packetBuffer[42] << 8;
      secsSince1900 |= (unsigned long)packetBuffer[43];
      return secsSince1900 - 2208988800UL + timeZone * SECS_PER_HOUR;
    }
  }
  Serial.println("No NTP Response :-(");
  return 0; // return 0 if unable to get the time
}

// send an NTP request to the time server at the given address
void sendNTPpacket(IPAddress &address)
{
  // set all bytes in the buffer to 0
  memset(packetBuffer, 0, NTP_PACKET_SIZE);
  // Initialize values needed to form NTP request
  // (see URL above for details on the packets)
  packetBuffer[0] = 0b11100011;   // LI, Version, Mode
  packetBuffer[1] = 0;     // Stratum, or type of clock
  packetBuffer[2] = 6;     // Polling Interval
  packetBuffer[3] = 0xEC;  // Peer Clock Precision
  // 8 bytes of zero for Root Delay & Root Dispersion
  packetBuffer[12] = 49;
  packetBuffer[13] = 0x4E;
  packetBuffer[14] = 49;
  packetBuffer[15] = 52;
  // all NTP fields have been given values, now
  // you can send a packet requesting a timestamp:
  Udp.beginPacket(address, 123); //NTP requests are to port 123
  Udp.write(packetBuffer, NTP_PACKET_SIZE);
  Udp.endPacket();
}
