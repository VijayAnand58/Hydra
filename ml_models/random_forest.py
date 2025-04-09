import pandas as  pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix

import joblib

df=pd.read_csv(r"C:\Users\vijay\Documents\Programming\Hydra\normal_data.csv",parse_dates=["timestamp"])

#print(df) #verify pandas loading

df.drop(columns=["timestamp","flask_active_users","flask_active_requests","process_virtual_memory_bytes","process_resident_memory_bytes","system_disk_usage_percent",],axis=1,inplace=True)

# print(df) #verify droped columns

# print(df["anomaly"].value_counts())
# number of anomalies are very less, so lets use SMOTE to bring balances

x = df.drop(columns=["anomaly"])
y = df["anomaly"]

# print(x)
# print(y)

#scale the data 
scaler = StandardScaler()
x_scaled = scaler.fit_transform(x)
joblib.dump(scaler, 'scaler.pkl')

x_train, x_test, y_train, y_test = train_test_split(
    x_scaled, y, test_size=0.2, random_state=42, stratify=y
)
from imblearn.over_sampling import SMOTE

smote = SMOTE(random_state=42)
x_train_res, y_train_res = smote.fit_resample(x_train, y_train)

model = RandomForestClassifier(class_weight="balanced",n_estimators=100,random_state=42)

model.fit(x_train_res,y_train_res)

# Predict
y_pred = model.predict(x_test)

# Evaluate
print("Classification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

#pickling the model using joblib

joblib.dump(model, 'rf_model.pkl')
print("Model saved successfully!")

