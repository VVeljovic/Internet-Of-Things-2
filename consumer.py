import paho.mqtt.client as paho
import re
from influxdb import InfluxDBClient

def on_connect(client,userdata,flags,rc):
	print("Connected with code:", rc)
	client.subscribe("sensors/nano33")
def on_message(client, userdata, msg):
	message = msg.payload.decode()
	print("Primljeno:", message)
	coords = {}
	if "X:" in message:
		parts = message.split()
		x = float(parts[1])
		y = float(parts[3])
		z = float(parts[5])
		label = parts[7]
		print(x)
		print(y)
		print(z)
		print(label)
		data = [
			{
				"measurement":"imu_data",
				"tags" : { "location": "arduino_nano_33_ble_sense_lite", "orientation" : label},
				"fields" : {"x":x, "y":y, "z":z}
			}]
		influxClient.write_points(data)

influxClient = InfluxDBClient(
	host = 'localhost',
	port = 8086,
	username='user',
	password = 'userpass',
	database='iotdb'
)
if {'name': 'iotdb'} not in influxClient.get_list_database():
	influxClient.create_database('iotdb')


client = paho.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
