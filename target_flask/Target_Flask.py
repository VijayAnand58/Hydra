from flask import Flask, Response,render_template
from prometheus_client import Counter, Summary, Gauge,CONTENT_TYPE_LATEST, generate_latest
import data_scraper_docker_api as dk
app = Flask(__name__)

# Metrics
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')
REQUEST_COUNT = Counter("ping_request_count", "Total requests to Flask app")
ACTIVE_REQUESTS = Gauge("flask_active_requests", "Number of concurrent active requests")
ACTIVE_USERS = Gauge("flask_active_users","Number of concurrrent users")

#system metrics
CPU_USAGE = Gauge("system_cpu_usage_percent", "CPU usage percentage")
MEMORY_USAGE = Gauge("system_memory_usage_percent", "Memory usage percentage")
DISK_USAGE = Gauge("system_disk_usage_percent", "Disk usage percentage")
# Network stats collection
PACKET_SENT = Gauge("network_packet_sent","Number of packets sent ")
PACKET_RECIVED = Gauge("network_packet_recieved","Number of packets recived")
NET_ERRORS_SENT = Gauge("network_errors_sent","network errors while packets are sent")
NET_ERRORS_RECIVED = Gauge("network_errors_recived","network errors while packets are recived")

# pre processor
@app.before_request
def before_request():
    """Increase active requests count when a request starts."""
    ACTIVE_REQUESTS.inc()


@app.after_request
def after_request(response):
    """Decrease active requests count when a request completes."""
    ACTIVE_REQUESTS.dec()
    return response
# Main app
@app.route("/", methods=["GET"])
@REQUEST_TIME.time()
def home():
    REQUEST_COUNT.inc() 
    return Response("Hello world", status=200)

@app.route("/login",methods=["GET"])
def login():
    REQUEST_COUNT.inc()
    ACTIVE_USERS.inc()
    return Response("Login successful",status=200)

@app.route("/logout",methods=["GET"])
def logout():
    REQUEST_COUNT.inc()
    ACTIVE_USERS.dec()
    return Response("Logout successful",status=200)

@app.route("/data",methods=["GET"])
@REQUEST_TIME.time()
def get_data():
    REQUEST_COUNT.inc()
    return render_template("index.html")

@app.route('/metrics')
@REQUEST_TIME.time()
def metrics():
    REQUEST_COUNT.inc()
    print("Usage metrics")

    CPU_USAGE.set(dk.get_cpu_percentage())
    MEMORY_USAGE.set(dk.get_memory_usage()) 
    DISK_USAGE.set(dk.get_disk_usage())  

    # net stats
    net_stat_dict=dk.netstats()
    net_stat_err=dk.get_dropped_packets()

    PACKET_SENT.set(net_stat_dict['transmitted'])
    PACKET_RECIVED.set(net_stat_dict['received'])
    NET_ERRORS_SENT.set(net_stat_err["dropped_trans"])
    NET_ERRORS_RECIVED.set(net_stat_err["dropped_rec"])
    
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
