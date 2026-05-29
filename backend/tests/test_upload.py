import io
import sys
from unittest.mock import MagicMock

_minio_instance = MagicMock()
_minio_instance.bucket_exists.return_value = True
_minio_instance.presigned_get_object.return_value = (
    "http://localhost:9000/firmware/firmware_v1.0.zip"
)

_minio_mod = MagicMock()
_minio_mod.Minio.return_value = _minio_instance

_mqtt_mod = MagicMock()
_mqtt_mod.Client.return_value = MagicMock()

sys.modules.setdefault("minio",            _minio_mod)
sys.modules.setdefault("paho",             MagicMock())
sys.modules.setdefault("paho.mqtt",        MagicMock())
sys.modules.setdefault("paho.mqtt.client", _mqtt_mod)

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_upload_success():
    """POST /upload with a valid file should return 200 and correct body."""
    response = client.post(
        "/upload",
        files={"file": ("firmware_v1.0.zip", io.BytesIO(b"fake-binary"), "application/zip")},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Successfully uploaded",
        "filename": "firmware_v1.0.zip",
    }
