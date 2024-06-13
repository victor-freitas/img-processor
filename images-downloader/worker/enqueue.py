import csv
import os
from rq import Queue
from redis import Redis
from tasks import download

# Configurações
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

# Conexões
redis_client = Redis(host=REDIS_HOST)
queue = Queue(connection=redis_client)


csv_file = '/app/input.csv'

with open(csv_file, 'r') as file:
    reader = csv.DictReader(file)
    for line in reader:
        slug = line['slug']
        profile_picture = line['profile_picture']
        queue.enqueue(download, slug=slug, picture_path=profile_picture)
        print(f"Enfileirado: {slug}")
