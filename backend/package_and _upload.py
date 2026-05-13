import os
import shutil
import argparse
import requests

API_URL        = "http://localhost:8000"
DEFAULT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "artifacts")


def create_package(folder: str, version: str) -> str:
    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder not found: {folder}")

    zip_name = f"firmware_{version}"
    print(f"Zipping '{folder}' → '{zip_name}.zip'")

    zip_path = shutil.make_archive(zip_name, "zip", folder)

    size = os.path.getsize(zip_path)
    print(f"Package created: {zip_path} ({size} bytes)")
    return zip_path


def upload_via_api(zip_path: str):
    print(f"Sending '{os.path.basename(zip_path)}' to API...")

    with open(zip_path, "rb") as f:
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": (os.path.basename(zip_path), f, "application/zip")},
        )

    if response.status_code == 200:
        print(f" API response: {response.json()}")
    else:
        print(f" Upload failed: HTTP {response.status_code}")
        print(f" {response.text}")


def main():
    parser = argparse.ArgumentParser(description="Package a folder and upload via API")
    parser.add_argument("--version", required=True, help="Firmware version e.g. 1.2.0")
    args = parser.parse_args()

    folder = os.path.join(os.path.dirname(__file__), "..", "artifacts")
    zip_path = create_package(folder, args.version)

    upload_via_api(zip_path)

    os.remove(zip_path)
    print(f"Cleaned up local zip: {zip_path}")


if __name__ == "__main__":
    main()