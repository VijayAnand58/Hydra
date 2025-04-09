import docker
import psutil
client=docker.from_env()

def get_container():
    try:
        return client.containers.get("flask_app")
    except docker.errors.NotFound:
        return None
    except docker.errors.APIError as e:
        print(f"Docker API error: {e}")
        return None

def get_cpu_percentage() -> float:
    container = get_container()
    if not container:
        return 0.0
    
    stats = container.stats(stream=False)

    cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
    system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]

    if system_delta > 0 and cpu_delta > 0:
        num_cpus = len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [])) or 1  
        cpu_percentage = (cpu_delta / system_delta) * num_cpus * 100 
        return round(cpu_percentage, 2)  
    
    return 0.0


def get_memory_usage() -> float:
    container = get_container()
    if not container:
        return 0.0

    stats = container.stats(stream=False)
    memory_usage = stats["memory_stats"]["usage"] - stats["memory_stats"]["stats"].get("cache", 0)
    memory_limit = stats["memory_stats"]["limit"]
    return round((memory_usage / memory_limit) * 100, 2) if memory_limit > 0 else 0.0

def get_disk_usage() -> float:
    """psutil gives host disk usage, not container disk usage."""
    return psutil.disk_usage('/').percent

def netstats() -> dict:
    container = get_container()
    if not container:
        return {"received": 0, "transmitted": 0}

    stats = container.stats(stream=False)
    networks = stats.get("networks", {})

    total_rx = sum(net.get("rx_bytes", 0) for net in networks.values())
    total_tx = sum(net.get("tx_bytes", 0) for net in networks.values())

    return {"received": total_rx, "transmitted": total_tx}

def get_dropped_packets() -> dict:
    container = get_container()
    if not container:
        return {"dropped_rec": 0, "dropped_trans": 0}

    stats = container.stats(stream=False)
    networks = stats.get("networks", {})

    dropped_rx = sum(net.get("rx_dropped", 0) for net in networks.values())
    dropped_tx = sum(net.get("tx_dropped", 0) for net in networks.values())

    return {"dropped_rec": dropped_rx, "dropped_trans": dropped_tx}
