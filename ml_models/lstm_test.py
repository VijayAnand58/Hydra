import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import classification_report, confusion_matrix

# Load your data
df = pd.read_csv("normal_data.csv")

# Drop unnecessary columns (adjust based on your file)
df.drop(columns=[
    "timestamp",
    "flask_active_requests",
    "flask_active_users",
    "process_virtual_memory_bytes",
    "process_resident_memory_bytes",
    "system_disk_usage_percent"
], inplace=True)

# Split features and label
X = df.drop(columns=["anomaly"])
y = df["anomaly"]

# Scale features
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Convert to 3D input for LSTM [samples, time steps, features]
# We'll assume one timestep per sample
X_lstm = np.reshape(X_scaled, (X_scaled.shape[0], 1, X_scaled.shape[1]))

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_lstm, y, test_size=0.2, random_state=42)

# Build LSTM model
model = Sequential()
model.add(LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.3))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# Train
early_stop = EarlyStopping(monitor='val_loss', patience=5)
model.fit(X_train, y_train, epochs=50, batch_size=16, validation_split=0.2, callbacks=[early_stop])

# Evaluate
y_pred = model.predict(X_test)
y_pred_binary = (y_pred > 0.5).astype("int32")

print("\nClassification Report:")
print(classification_report(y_test, y_pred_binary))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_binary))
