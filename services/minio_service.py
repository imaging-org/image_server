from minio import Minio
from utils.config import MinioConfig


class MinioService:
    def __init__(self):
        self._client = Minio(
            "localhost:9000",
            access_key=MinioConfig.ACCESS_KEY,
            secret_key=MinioConfig.SECRET_KEY,
            secure=False
        )

        if not self._client.bucket_exists(MinioConfig.BUCKET_NAME):
            self._client.make_bucket(MinioConfig.BUCKET_NAME)

    def put_file(self, file_path, object_key):
        print("Putting file to Minio")
        self._client.fput_object(
            MinioConfig.BUCKET_NAME,
            file_path=file_path,
            object_name=object_key
        )
        print("Successfully put file to Minio")

    def delete_file(self, object_key):
        self._client.remove_object(MinioConfig.BUCKET_NAME, object_name=object_key)

    def reset_bucket(self):
        try:
            objects = list(self._client.list_objects(MinioConfig.BUCKET_NAME))
            for obj_ in objects:
                self.delete_file(obj_.object_name)
            self._client.remove_bucket(MinioConfig.BUCKET_NAME)
            self._client.make_bucket(MinioConfig.BUCKET_NAME)
        except Exception as e:
            print(f"Error in resetting minio : {e}")
            return "Failed"
        else:
            return "Success"
