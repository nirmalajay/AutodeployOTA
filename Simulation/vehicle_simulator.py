import paho.mqtt.client as mqtt
import json
import requests
import os
import re
from packaging.version import Version, InvalidVersion

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT   = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC  = "vehicle/ota"
DOWNLOAD_DIR = "./downloads"

CURRENT_VERSION = Version("1.0.0")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def parse_version_from_filename(filename: str):

    match = re.search(r"(\d+\.\d+\.\d+)", filename)
    if match:
        try:
            return Version(match.group(1))
        except InvalidVersion:
            return None
    return None


def on_connect(client, userdata, flags, reason_code, properties):
    if not reason_code.is_failure:
        print(f"[Vehicle]  Connected to MQTT broker")
        print(f"[Vehicle]  Current firmware version: {CURRENT_VERSION}")
        client.subscribe(MQTT_TOPIC)
        print(f"[Vehicle]  Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"[Vehicle]  Connection failed: {reason_code}")


def on_message(client, userdata, msg):
    global CURRENT_VERSION
    print(f"\n[Vehicle] Received message on '{msg.topic}'")

    try:
        payload = json.loads(msg.payload.decode())

        if payload.get("event") != "new_firmware":
            return

        filename = payload["filename"]
        download_url = payload["download_url"]
        size = payload.get("size", "unknown")

        print(f"[Vehicle]  New firmware available: {filename} ({size} bytes)")

        # --- Version check ---
        new_version = parse_version_from_filename(filename)

        if new_version is None:
            print(f"Could not parse version from filename: '{filename}'")
            print(f"Name your files like: firmware_1.2.0.bin")
            return

        print(f"Version check: current={CURRENT_VERSION}  →  incoming={new_version}")

        if new_version <= CURRENT_VERSION:
            print(f"Already up to date (v{CURRENT_VERSION}). Skipping download.")
            return
        else:
            print(f"Newer version found! Downloading v{new_version}...")
            
            # --- Handle internal Docker hostname locally ---
            headers = {}
            if "minio:9000" in download_url:
                download_url = download_url.replace("minio:9000", "localhost:9000")
                headers["Host"] = "minio:9000"

            response = requests.get(download_url, timeout=30, headers=headers)

            if response.status_code == 200:
                save_path = os.path.join(DOWNLOAD_DIR, filename)
                with open(save_path, "wb") as f:
                    f.write(response.content)
                print(f"Saved to: {save_path}")

                print(f"[Applying update v{CURRENT_VERSION} → v{new_version}...")
                CURRENT_VERSION = new_version
                print(f"Update complete! Now running v{CURRENT_VERSION}")
            else:
                print(f" Download failed: HTTP {response.status_code}")

    except json.JSONDecodeError:
        print(f"Could not parse message payload")
    except Exception as e:
        print(f"Unexpected error: {e}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print(f"[Vehicle] Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
client.connect(MQTT_BROKER, MQTT_PORT)

client.loop_forever()
