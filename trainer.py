from influxdb import InfluxDBClient
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
from tensorflow import keras
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

client = InfluxDBClient(host='localhost', port = 8086, database='iotdb')
query = 'SELECT x, y, z, orientation FROM imu_data'
result = client.query(query)

points = list(result.get_points())
df = pd.DataFrame(points)

print(f"Ukupno podataka: {len(df)}")
print(df.head())

df = df.dropna()

x = df[['x', 'y', 'z']].values
y = df['orientation'].values

print(x)
print(y)

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

y_categorical = keras.utils.to_categorical(y_encoded)

x_train, x_test, y_train, y_test = train_test_split(
      x, y_categorical,
      test_size=0.2,
      random_state=42,
      stratify=y_encoded  
  )
num_classes = len(label_encoder.classes_)

model = keras.Sequential([
      keras.layers.Input(shape=(3,)),  
      keras.layers.Dense(16, activation='relu'),
      keras.layers.Dropout(0.2),
      keras.layers.Dense(8, activation='relu'),
      keras.layers.Dense(num_classes, activation='softmax')
  ])

model.compile(
      optimizer='adam',
      loss='categorical_crossentropy',
      metrics=['accuracy']
  )
print(f"Train set: {len(x_train)}")

print("\n" + "="*60)
print("TRENIRANJE")
print("="*60)

history = model.fit(
      x_train, y_train,
      epochs=50,
      batch_size=32,
      validation_split=0.2,
      verbose=1
  )
print("\n" + "="*60)
print("EVALUACIJA")
print("="*60)
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\n✅ Test Loss: {test_loss:.4f}")
print(f"✅ Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
print("\n" + "="*60)

model.save('imu_orientation_model.h5')
print("✅ Model sačuvan: imu_orientation_model.h5")
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)

print("\n" + "="*60)
print("TEST")
print("="*60)
def predict_orientation(x_val, y_val, z_val):
    sample = np.array([[x_val, y_val, z_val]])
    pred = model.predict(sample, verbose=0)
    pred_class = label_encoder.classes_[np.argmax(pred)]
    confidence = np.max(pred)
    print(f"X={x_val:.2f}, Y={y_val:.2f}, Z={z_val:.2f} → {pred_class} ({confidence:.2%})")
predict_orientation(0.02, -0.01, 0.98)   # horizontal
predict_orientation(0.95, 0.03, 0.05)    # vertical
predict_orientation(0.65, 0.10, 0.70)    # diagonal
print("\n✅ Gotovo!")