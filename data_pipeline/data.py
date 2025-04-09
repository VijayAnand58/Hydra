import os
import time
import requests
import pandas as pd
from datetime import datetime,timedelta
import random
import subprocess

# Prometheus API endpoint
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"

RUN_DURATION_MINUTES = 60 #this indicates the total time the program is goona run

CMD__CPU_KILL="wsl docker run --rm -v /var/run/docker.sock:/var/run/docker.sock   gaiaadm/pumba stress --duration 59s"
#Stress cpu for 59 seconds, affect ram too
CMD_NET_KILL="docker run -it --rm --net=host   -v /var/run/docker.sock:/var/run/docker.sock   gaiaadm/pumba netem --duration 59s   loss --percent 100 --correlation 100 re2:flask_app"
#packet loss for 59 seconds

# Metrics to track
metrics = [
    "flask_active_requests",
    "flask_active_users",
    "rate(request_processing_seconds_sum[30s]) / rate(request_processing_seconds_count[30s])",
    "process_virtual_memory_bytes",
    "process_resident_memory_bytes",
    "process_cpu_seconds_total",
    "system_cpu_usage_percent",
    "system_memory_usage_percent",
    "system_disk_usage_percent",
    "rate(network_packet_recieved[30s])/rate(network_packet_sent[30s])",
]
# Generate 4 random anomaly times (1 per 10 mins)
start_time = datetime.now()
quarters = [start_time + timedelta(minutes=10 * i) for i in range(6)]
anomaly_times = [
    q_start + timedelta(seconds=random.randint(0, 9 * 60))
    for q_start in quarters
]
print("Anomalies time are generated it includes",anomaly_times)
print("Scheduled Anomalies:")
for i, t in enumerate(anomaly_times):
    print(f"number of 10 mins: {i+1}: {t.strftime('%H:%M:%S')}")

def trigger_anomaly(count):
    print("Running pumba")
    try:
        if count%2==0:
            print("CPU kill")
            subprocess.Popen(CMD__CPU_KILL,shell=True)
        else:
            print("Net kill")
            subprocess.Popen(CMD_NET_KILL,shell=True)
    except Exception as e:
        print("pumba failed")
        return 0

def fetch_metrics(anomaly=False):
    data_row = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),"anomaly":int(anomaly)}
    
    for metric in metrics:
        response = requests.get(PROMETHEUS_URL, params={"query": metric})
        result = response.json()

        if "data" in result and "result" in result["data"] and result["data"]["result"]:
            data_row[metric] = float(result["data"]["result"][0]["value"][1])
        else:
            data_row[metric] = 0  # Default value if metric not available

    return data_row

# State
anomaly_active = False
anomaly_end_time = None

# Collect normal data for 1 minute (12 samples, 5 seconds interval)
print("Collecting data for 1 hour")
endtime=start_time+timedelta(minutes=RUN_DURATION_MINUTES)

try:
    count_anomaly=0
    while datetime.now() < endtime:
        now = datetime.now()

        # Start anomaly if it's time
        for anomaly_time in anomaly_times:
            if not anomaly_active and anomaly_time <= now < anomaly_time + timedelta(seconds=5):
                print("Anomally starts")
                trigger_anomaly(count=count_anomaly)
                print("Time delay")
                time.sleep(13)
                print("Time ended")
                count_anomaly+=1 #increase the anomaly counter after each run of it
                anomaly_active = True # making the anomalay session active for the fetch info to know
                anomaly_end_time = now + timedelta(seconds=70) #to end this session
                break

        # Turn off anomaly after duration
        if anomaly_active and now >= anomaly_end_time:
            anomaly_active = False
            print("Anomaly ended.")

        # Collect and save data
        data = fetch_metrics(anomaly=anomaly_active)
        pd.DataFrame([data]).to_csv("normal_data.csv", mode="a", index=False, header=not pd.io.common.file_exists("normal_data.csv"))

        print(f"[{data['timestamp']}] Anomaly: {data['anomaly']}")
        time.sleep(5) # interval 5 seconds to again quey the data

except KeyboardInterrupt:
    print("Collection stopped.")


