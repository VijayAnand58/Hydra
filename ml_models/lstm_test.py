import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
# function to create a time window
def create_sequences(data, labels, look_back=1):
    
    X_sequences, y_sequences = [], []
    for i in range(len(data) - look_back):
        X_sequences.append(data[i:(i + look_back)])
        y_sequences.append(labels[i + look_back]) # Predict anomaly at the end of the sequence
    return np.array(X_sequences), np.array(y_sequences)

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
#sequnce lookback for LSTM
look_back=5
# Split features and label
X = df.drop(columns=["anomaly"])
y = df["anomaly"]

# Scale features
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)
# Create sequences for LSTM
X_sequences, y_sequences = create_sequences(X_scaled, y.values, look_back)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_sequences, y_sequences, test_size=0.2, random_state=42, stratify=y_sequences)

X_train_flat = X_train.reshape(X_train.shape[0], -1)

smote = SMOTE(random_state=42)
X_train_resampled_flat, y_train_resampled = smote.fit_resample(X_train_flat, y_train)

# Reshape back to 3D for LSTM
X_train_resampled = X_train_resampled_flat.reshape(X_train_resampled_flat.shape[0], look_back, X.shape[1])

# Build LSTM model
model = Sequential()
model.add(LSTM(64, input_shape=(X_train_resampled.shape[1], X_train_resampled.shape[2]), return_sequences=False))
model.add(Dropout(0.3))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid')) # Binary classification output


model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

# Train
early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
history = model.fit(
    X_train_resampled, y_train_resampled,
    epochs=15, 
    batch_size=32,
    validation_split=0.2, 
    callbacks=[early_stopping],
    verbose=1
)
# Evaluate
y_pred = model.predict(X_test)
y_pred_binary = (y_pred > 0.5).astype("int32")

print("\nClassification Report:")
print(classification_report(y_test, y_pred_binary))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred_binary))
