from datetime import timedelta
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from minio import Minio
import paho.mqtt.client as mqtt
import json
import os
import io


minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "localhost:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "udumalpet"),
    secure=False
)

mqtt_client = mqtt.Client()
mqtt_client.connect(os.getenv("MQTT_BROKER", "localhost"), 1883)
mqtt_client.loop_start()

BUCKET_NAME = "firmware"

if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

app = FastAPI()



class UploadResponse(BaseModel):
    """Response schema for a successful firmware upload."""
    message: str
    filename: str



def get_presigned_url(filename: str) -> str:
    """Generate a 10-minute presigned download URL for a file in MinIO."""
    return minio_client.presigned_get_object(
        BUCKET_NAME,
        filename,
        expires=timedelta(minutes=10),
    )

def notify_vehicles(filename: str, size: int):
    """Publish an OTA notification to all subscribed vehicles via MQTT."""
    msg = {
        "event": "new_firmware",
        "filename": filename,
        "size": size,
        "download_url": get_presigned_url(filename),
    }
    mqtt_client.publish("vehicle/ota", json.dumps(msg))


# --- Routes ---

# @app.get("/latest")
# async def get_latest():
#     """Returns the most recently uploaded firmware from MinIO."""
#     objects = list(minio_client.list_objects(BUCKET_NAME))
#     if not objects:
#         return {"error": "No firmware files found in bucket"}

#     latest = max(objects, key=lambda o: o.last_modified)

#     return {
#         "version": latest.object_name,
#         "firmware": {
#             "name": latest.object_name,
#             "size": latest.size,
#             "url": get_presigned_url(latest.object_name),
#             "last_modified": str(latest.last_modified),
#         }
#     }

@app.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    """Upload firmware to MinIO and notify vehicles via MQTT."""
    data = await file.read()
    minio_client.put_object(BUCKET_NAME, file.filename, io.BytesIO(data), len(data))
    notify_vehicles(file.filename, len(data))
    return UploadResponse(message="Successfully uploaded", filename=file.filename)