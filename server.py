from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from influxdb import InfluxDBClient
import paho.mqtt.client as mqtt


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

influxClient = InfluxDBClient(
	host='localhost',
	port=8086,
	username='user',
	password='userpass',
	database='iotdb'
)

def on_connect(client,userdata,flags,rc):
	print("Connected with code:", rc)
	client.subscribe("notification")

@app.route("/set-threshold", methods=["POST"])
def set_threshold():
	data = request.get_json()
	threshold = data.get("threshold")
	if threshold is not None:
		mqttClient.publish("configuration", str(threshold))
		print("Poslat threshold:", threshold)
		return jsonify({"status": "ok", "threshold": threshold})
	return jsonify({"status": "error", "message": "Threshold nije prosleđen"}), 400

@app.route("/set-anomaly", methods=['POST'])
def set_anomaly():
	data = request.get_json()
	anomaly = data.get("anomaly")
	mqttClient.publish("anomaly", anomaly)
	return jsonify({"status": "ok", "anomaly": anomaly})


@app.route('/simulate')
def simulate():
	socketio.emit("new-data", {"data": "X: 0.12 Y: -0.45 Z: 9.81 VERTICAL"})
	return "OK"

@app.route('/data')
def get_data():
	data = influxClient.query("SELECT * FROM imu_data")
	points = list(data.get_points())
	return jsonify(points)

@socketio.on('connect')
def handle_connect():
	print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
	print('Client disconnected')

def on_mqtt_message(client, userdata, msg):
	payload = msg.payload.decode()
	print("MQTT poruka:", payload)
	socketio.emit("new-data", {"data": payload})

mqttClient = mqtt.Client()
mqttClient.on_message = on_mqtt_message
mqttClient.on_connect = on_connect
mqttClient.connect("localhost", 1883, 60)
mqttClient.loop_start()


if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', port=5000)
