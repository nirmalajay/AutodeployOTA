import requests
url = "http://localhost:9000/firmware/firmware_1.1.0.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20260513%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260513T100003Z&X-Amz-Expires=600&X-Amz-SignedHeaders=host&X-Amz-Signature=c6130262006e8b2f785a1ebacd03dfdf917a1c4e69867aa2a2825128c4d53ed8"
try:
    r = requests.get(url)
    print(r.status_code)
except Exception as e:
    print(e)
