import io
import sys
from unittest.mock import MagicMock

# ── Mock external modules via sys.modules BEFORE importing main ───────────
#
# Why sys.modules instead of patch():
#   minio imports argon2-cffi (a compiled C extension).
#   On CI runners the .so can be the wrong architecture → ImportError.
#   By injecting MagicMock objects into sys.modules we bypass the real
#   import entirely — the C extension never loads.

_minio_instance = MagicMock()
_minio_instance.bucket_exists.return_value = True
_minio_instance.presigned_get_object.return_value = (
    "http://localhost:9000/firmware/firmware_v1.0.zip"
)

_minio_mod = MagicMock()
_minio_mod.Minio.return_value = _minio_instance

_mqtt_instance = MagicMock()
_mqtt_mod = MagicMock()
_mqtt_mod.Client.return_value = _mqtt_instance

sys.modules.setdefault("minio",             _minio_mod)
sys.modules.setdefault("paho",              MagicMock())
sys.modules.setdefault("paho.mqtt",         MagicMock())
sys.modules.setdefault("paho.mqtt.client",  _mqtt_mod)

# ── Now it's safe to import main (no real minio/paho code runs) ───────────
from fastapi.testclient import TestClient
from main import app, UploadResponse

client = TestClient(app)


# ── API test ──────────────────────────────────────────────────────────────

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


# ── Pydantic schema tests ─────────────────────────────────────────────────

def test_upload_response_conforms_to_schema():
    """API response must parse into the UploadResponse Pydantic model."""
    response = client.post(
        "/upload",
        files={"file": ("firmware_v2.0.zip", io.BytesIO(b"data"), "application/zip")},
    )
    model = UploadResponse(**response.json())
    assert isinstance(model.message, str)
    assert isinstance(model.filename, str)
    assert model.filename == "firmware_v2.0.zip"


def test_upload_response_schema_rejects_bad_types():
    """Pydantic must reject wrong field types."""
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        UploadResponse(message=123, filename=None)


def test_upload_response_schema_requires_all_fields():
    """Pydantic must reject a payload with a missing required field."""
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        UploadResponse(message="ok")   # missing 'filename'

