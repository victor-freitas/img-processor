import os
import redis
import json
from rq import Queue
from rq.decorators import job
import os
import requests
import tempfile
import mimetypes
import boto3
import pyodbc
import time
from minio_manager import MinioManager, SpacesManager
from urllib.parse import unquote, urlparse


REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')

redis_client = redis.Redis(host=REDIS_HOST)


sql_server_conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={os.environ.get("SQL_HOST_PROCESS_PF_IMAGES")};'
    f'DATABASE={os.environ.get("SQL_PROCESS_PF_IMAGES_DB")};'
    f'UID={os.environ.get("SQL_USR_PROCESS_PF_IMAGES")};'
    f'PWD={os.environ.get("SQL_PW_PROCESS_PF_IMAGES")};'
)

def extract_file_extension(url):
    parsed_url = urlparse(url)
    file_path = unquote(parsed_url.path)
    file_extension = file_path.split(".")[-1] if "." in file_path else ""
    return file_extension

def download_image_from_minio(slug, path):
    start = time.time()
    file_extension = extract_file_extension(path)
    mm = MinioManager()
    file_url = mm.generate_url(
        'images', path
    )

    if not file_url:
        return
    print(f"Downloading file: {file_url}")

    response = requests.get(file_url)
    response.raise_for_status()
    if not file_extension:
        content_type = response.headers.get("Content-Type")
        file_extension = mimetypes.guess_extension(content_type)
    if file_extension:
        file_extension = file_extension.replace(".", "")
    else:
        file_extension = "jpeg"
    folder_name = "images"
    storage_file_path = f"{folder_name}/{slug}.{file_extension}"
    print(f"Saving a {file_extension}: {storage_file_path}")
    # create a temp file to upload
    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name
        client = boto3.client(
            "s3",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            endpoint_url=os.environ.get("DO_BUCKET_ENDPOINT")
        )

        bucket_name = os.environ.get("DO_BUCKET_NAME")
        client.upload_file(temp_file_path, bucket_name, storage_file_path)
    print(f'Download time: {time.time() - start}')
    return storage_file_path

def update_database(path, slug):
    start = time.time()
    # conn = pyodbc.connect(sql_server_conn_str)
    # cursor = conn.cursor()
    update_query = f"""
        UPDATE [DB_DATA_LAKE].[dbo].[TB_LKD_INT_PF_PHOTOS]
        SET PHOTO_PATH = '{path}'
        WHERE PUBLIC_ID = '{slug}'
    """
    # cursor.execute(update_query)
    # conn.commit()
    # cursor.close()
    # conn.close()
    redis_client.rpush('update_query', json.dumps(update_query))
    print(f'DB time: {time.time() - start}')

def process_image(slug, image_path):
    start = time.time()
    file_path = download_image_from_minio(slug, image_path)
    update_database(file_path, slug)
    print(f'TOTAL TIME: {time.time() - start}')


def bulk_update():
    start = time.time()
    counter = 0
    sqls = []
    while counter < 999:
        counter += 1
        query = redis_client.rpop('update_query')
        if not query:
            break
        sqls.append(json.loads(query))
    print(f'Running {len(sqls)} queries:')
    if not sqls:
        print('No sqls')
        return
    txt_query = ';'.join(sqls)
    conn = pyodbc.connect(sql_server_conn_str)
    cursor = conn.cursor()
    cursor.execute(txt_query)
    conn.commit()
    cursor.close()
    conn.close()
    print(f'Bulk update time: {time.time() - start}')


@job('default', connection=redis_client)
def download(slug, picture_path):
    print(f'Download - slug: {slug} - path: {picture_path}')
    process_image(slug=slug, image_path=picture_path)

if __name__ == "__main__":
    print("Worker is running...")
