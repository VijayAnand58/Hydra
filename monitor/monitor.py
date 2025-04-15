import time
import requests
from datetime import datetime,timedelta
import joblib
import warnings

import asyncio
import threading
from discord_alert import get_bot, get_send_function, get_token

bot = get_bot()
send_discord_message = get_send_function()
token = get_token()



warnings.filterwarnings("ignore")
# Prometheus API endpoint
PROMETHEUS_URL = "http://localhost:9090/api/v1/query"

metrics = [
    "rate(request_processing_seconds_sum[30s]) / rate(request_processing_seconds_count[30s])",
    "process_cpu_seconds_total",
    "system_cpu_usage_percent",
    "system_memory_usage_percent",
    "rate(network_packet_recieved[30s])/rate(network_packet_sent[30s])",
]

scaler = joblib.load('scaler.pkl')


def fetch_metrics():
    data_row={}
    for metric in metrics:
        response = requests.get(PROMETHEUS_URL, params={"query": metric})
        result = response.json()

        if "data" in result and "result" in result["data"] and result["data"]["result"]:
            data_row[metric] = float(result["data"]["result"][0]["value"][1])
        else:
            data_row[metric] = 0
    data_row_list=list(data_row.values())
    print(data_row)
    data_scaled=scaler.transform([data_row_list])
    return data_scaled



# Load the saved model
loaded_model = joblib.load('rf_model.pkl')

#get action.py
import action as ac

sending_message="""Server acting anonomously,
please attend to it, for now an additional container is springed up"""

def run_bot():
    bot.run(token)

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()

    while True:
        try:
            data = fetch_metrics()
            pred = loaded_model.predict(data)

            if int(pred[0]) == 1:
                future = asyncio.run_coroutine_threadsafe(send_discord_message(sending_message), bot.loop)
                try:
                    future.result(timeout=5)
                    print("Message sent to Discord!")
                except Exception as e:
                    print(f"Failed to send message: {e}")
                ac.run_duplicate_container()

            time.sleep(5)
        except KeyboardInterrupt:
            break
