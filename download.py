import os
from pathlib import Path

import pika

from celery import Celery
from minio import Minio

from config import *
from models import *

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Celery("tasks", broker=CELERY_BROKER, backend=CELERY_BACKEND)

engine = create_engine("sqlite:///test_db.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Клиент MinIO
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)

@app.task
def upload_file(file_path: str):
    object_name = file_path.split("/")[-1]
    """1. Загружает файл в MinIO"""
    minio_client.fput_object(MINIO_BUCKET, object_name, file_path)

    dl_file = session.query(File).filter_by(file_name=object_name).first()
    if dl_file:
        dl_file.download = 1  # Увеличиваем счетчик
        print(f"Обновлена запись: {dl_file}")
    else:
        # 3. Если не существует - откатываемся
        session.rollback()
        print(f"Файл {object_name} не найден. Изменения не применены.")

    # 4. Фиксируем изменения
    session.commit()
    session.close()

    """2. Уведомляет внешний сервис через AMQP"""
    """AMQP в параметре RABBITMQ_URL_NOTIFY """
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL_NOTIFY))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=f"В MinIO загружен новый файл: {object_name}",
    )

    connection.close()

@app.task
def process_file(file_path: str):
    folder_to_download = ".\\dl_files" # У меня просто локальная папка для скачанных файлов
    os.makedirs(folder_to_download, exist_ok=True)

    file_name = os.path.basename(file_path)
    local_path = os.path.join(folder_to_download, file_name)

    # Копируем файл в нужную директорию
    if os.path.exists(file_path):
        with open(file_path, 'rb') as src, open(local_path, 'wb') as dst:
            dst.write(src.read())
        dl_file = session.query(File).filter_by(file_name=file_name).first()
        if dl_file:
            dl_file.download = 1  # Увеличиваем счетчик
            print(f"Обновлена запись: {dl_file}")
        else:
            # 3. Если не существует - откатываемся
            session.rollback()
            print(f"Файл {file_name} не найден. Изменения не применены.")

        # 4. Фиксируем изменения
        session.commit()
        session.close()

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='file_notifications')
    channel.basic_publish(exchange='',
            routing_key='file_notifications',
            body=f"В MinIO загружен новый файл: {file_name}")