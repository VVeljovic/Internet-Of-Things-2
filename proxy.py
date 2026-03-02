import serial 
import paho.mqtt.client as mqtt

#ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser = serial.Serial('COM5', 115200, timeout=1)

client = mqtt.Client()
client.connect("localhost",1883,60)

while True:
	line = ser.readline().decode(errors='ignore').strip()
	if line:
		print("Primljeno ", line)
		client.publish("sensors/nano33", line)
