
import docker
import time

def run_duplicate_container():
    client = docker.from_env()

    # Make sure the image is built already
    image_name = "flask_app"  # Docker Compose built this image

    container_name = "flask_app_clone"

    # Remove if already running
    try:
        existing = client.containers.get(container_name)
        existing.remove(force=True)
    except docker.errors.NotFound:
        pass

    # Run new container
    print("Added time dealy to new container spin for 80 seconds")
    time.sleep(80)
    print("Time dealy ended")
    
    container = client.containers.run(
        image=image_name,
        name=container_name,
        command=None,  # If your image has a CMD already set
        detach=True,
        network="target_flask_monitoring",  # ← match your docker-compose network
        volumes={
            "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"},
            "/usr/bin/docker": {"bind": "/usr/bin/docker", "mode": "ro"},
        },
        ports={"5000/tcp": None},  # Don’t expose to host (optional)
    )

    print(f"Started container: {container.name}")

    # Let it run for 5 mins then stop
    time.sleep(5 * 60)
    container.remove(force=True)
    print("Container stopped and removed.")