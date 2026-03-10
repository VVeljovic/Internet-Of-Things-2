import paho.mqtt.client as paho
from influxdb import InfluxDBClient
from datetime import datetime
import numpy as np
import tensorflow as tf
import pickle

model = tf.keras.models.load_model('imu_orientation_model.h5')
with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

def predict_orientation(x, y, z):
    sample = np.array([[x, y, z]])
    pred = model.predict(sample, verbose=0)
    return label_encoder.classes_[np.argmax(pred)]

BATCH_SIZE = 10

def add_to_buffer(x,y,z,orientation):
	data = {
		"measurement" : "imu_data",
		"tags" : {"orientation" : orientation},
		"fields" : {
		"x": x,
		"y": y,
		"z": z},
		"time" : datetime.utcnow().isoformat()
		}
	if orientation == "VERTICAL":
		vertical_array.append(data)
		if len(vertical_array) == BATCH_SIZE:
			influxClient.write_points(vertical_array)
			print("vertical buffer stored")
			vertical_array.clear()
	
	elif orientation == "HORIZONTAL":
		horizontal_array.append(data)
		if len(horizontal_array) == BATCH_SIZE:
			influxClient.write_points(horizontal_array)
			print("horizontal buffer stored")
			horizontal_array.clear()
			
	else:
		diagonal_array.append(data)
		if len(diagonal_array) == BATCH_SIZE:
			influxClient.write_points(diagonal_array)
			print("diagonal buffer stored")
			diagonal_array.clear()

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
		label = predict_orientation(x, y, z)
		print(x)
		print(y)
		print(z)
		print(label)
		if label == "VERTICAL":
			print('alert')
		add_to_buffer(x,y,z,label)

influxClient = InfluxDBClient(
	host = 'localhost',
	port = 8086,
	username='user',
	password = 'userpass',
	database='iotdb'
)
if {'name': 'iotdb'} not in influxClient.get_list_database():
	influxClient.create_database('iotdb')

horizontal_array = []
vertical_array = []
diagonal_array = []
client = paho.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
