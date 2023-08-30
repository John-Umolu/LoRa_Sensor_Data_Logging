#include <SoftwareSerial.h>
#include <DHT.h>
#include <DHT_U.h>

// create a new serial com port
SoftwareSerial mySerial(2, 3); // RX, TX

// DHT11 Temperature and humidity sensor is connected to arduino analoque pin A0
#define DHTPIN A0
#define DHTTYPE DHT11 

DHT dht(DHTPIN, DHTTYPE);

// MQ-135 Gas sensor is connected to arduino analoque pin A1
int gasPin=A1;

// Flame sensor is connected to arduino analoque pin 4
int flamePin=4;

// create the string variables
String sensorvaluestr;
String datalength;
String mymessage;
//

void setup()
{
  // set the data rate for the Serial and SoftwareSerial ports
  mySerial.begin(115200);
  Serial.begin(9600);
  dht.begin();

  // configure the arduino input and output pins
  pinMode(gasPin, INPUT);
  pinMode(DHTPIN, INPUT);
  pinMode(flamePin, INPUT);
}

void loop() {
  // store all sensor data to a string
  sensorvaluestr = String(analogRead(gasPin)) + "A" + String(dht.readTemperature(), 0) + "A" + String(dht.readHumidity(), 0) + "A" + String(digitalRead(flamePin));

  // get the total string length
  datalength = String(sensorvaluestr.length());

  // define the LoRa module message to be sent
  mymessage = "AT+SEND=102," + datalength + "," + sensorvaluestr + "\r\n";

  // send message
  mySerial.println(mymessage);
  Serial.println(mymessage);

  // delay for 3 seconds
  delay(3000);
}
