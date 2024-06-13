import os
import boto3

MINIO_ACCESS_KEY = os.environ['MINIO_ACCESS_KEY']
MINIO_SECRET_KEY = os.environ['MINIO_SECRET_KEY']
MINIO_ENDPOINT = os.environ['MINIO_ENDPOINT']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY= os.environ['AWS_SECRET_ACCESS_KEY']
DO_BUCKET_ENDPOINT = os.environ['DO_BUCKET_ENDPOINT']
MINIO_BUCKET_NAME = os.environ['MINIO_BUCKET_NAME']

class MinioManager:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            endpoint_url=MINIO_ENDPOINT
        )
        self.expiration_time = 3600

    def get_s3_client(self):
        return self.s3

    def find_file_content(self, key, bucket_name, path):
        try:
            image_path = self.s3.list_objects_v2(
                Bucket=bucket_name, Prefix=f"{path}/{key}", MaxKeys=1)["Contents"][0]['Key']
            url = self.generate_url(bucket_name, image_path)
            return url
        except (KeyError, IndexError):
            return None

    def generate_url(self, bucket_name, file_path):
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': file_path},
                ExpiresIn=self.expiration_time,
                HttpMethod='GET'
            )
            return url
        except Exception:
            return None


class SpacesManager(MinioManager):
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            endpoint_url=DO_BUCKET_ENDPOINT
        )
        self.expiration_time = 3600

