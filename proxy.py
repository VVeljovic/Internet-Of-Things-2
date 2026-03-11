import serial
import paho.mqtt.client as mqtt

#ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
ser = serial.Serial('COM6', 115200, timeout=1)

def on_message(client, userdata, msg):
	if msg.topic == "configuration":
		value = msg.payload.decode().strip()
		ser.write(f"{value}\n".encode())
		print("Poslato na Arduino:", value)

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883, 60)
client.subscribe("configuration")
client.loop_start()

while True:
	line = ser.readline().decode(errors='ignore').strip()
	if line:
		print("Primljeno ", line)
		client.publish("sensors/nano33", line)
