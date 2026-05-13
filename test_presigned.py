from minio import Minio
client = Minio("fake-host:9000", access_key="minioadmin", secret_key="udumalpet", secure=False)
try:
    url = client.presigned_get_object("firmware", "test.bin")
    print(url)
except Exception as e:
    print(e)
