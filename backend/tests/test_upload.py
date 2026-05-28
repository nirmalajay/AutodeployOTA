import io
from unittest.mock import MagicMock, patch

# Patch MinIO and MQTT before `main` is imported (they connect at module level)
with patch("minio.Minio") as mock_minio_cls, \
     patch("paho.mqtt.client.Client") as mock_mqtt_cls:

    mock_minio_instance = MagicMock()
    mock_minio_instance.bucket_exists.return_value = True
    mock_minio_instance.presigned_get_object.return_value = "http://localhost:9000/firmware/firmware_v1.0.zip"
    mock_minio_cls.return_value = mock_minio_instance

    mock_mqtt_instance = MagicMock()
    mock_mqtt_cls.return_value = mock_mqtt_instance

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


def test_upload_no_file_returns_422():
    """POST /upload without a file should return 422 Unprocessable Entity."""
    response = client.post("/upload")
    assert response.status_code == 422


def test_upload_different_filename():
    """Filename in the response must match what was uploaded."""
    response = client.post(
        "/upload",
        files={"file": ("update_2.0.bin", io.BytesIO(b"data"), "application/octet-stream")},
    )
    assert response.status_code == 200
    assert response.json()["filename"] == "update_2.0.bin"
