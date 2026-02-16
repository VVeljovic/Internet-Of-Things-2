from influxdb import InfluxDBClient
import pandas as pd

client = InfluxDBClient(host='localhost', port = 8086, database='iotdb')
query = 'SELECT x, y, z, orientation FROM imu_data'
result = client.query(query)

points = list(result.get_points())
df = pd.DataFrame(points)

print(f"Ukupno podataka: {len(df)}")
print(df.head())

x = df[['x', 'y', 'z']].values
y = df['orientation'].values

print(x)
print(y)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

y_categorical = keras.utils.to_categorical(y_encoded)
x_train, x_text, y_train, y_test = train_test_split(x, y_categorical, test_size=0.2,random_state=42, stratify=encoded)

print(f"Train set: {len(x_train)}")
