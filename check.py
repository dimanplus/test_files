from config import *
from models import *
from download import *

import os
import time

# в моём случае использую watchdog, но для Celery код будет рядом
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import pika

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_URL_FILES))
channel = connection.channel()
channel.queue_declare(queue='new_files')

engine = create_engine("sqlite:///test_db.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:  # проверяем, что это не создание папок
            file_name = os.path.basename(event.src_path)
            file_path = event.src_path
            print(f"Обнаружен новый файл: {file_name}")
            channel.basic_publish(exchange='',
                      routing_key='new_files',
                      body=f"{file_name}")
            try:
                new_file = File(file_name=file_name, download=0)
                session.add(new_file)
                session.commit()
                print(f"В БД обавлен файл: {new_file}")
                process_file(file_path) # это для моего локального варианта

                # upload_file.delay(file_path) # это для рабочего MinIO
                ''' 
                НО... тогда придется запустить воркер отдельно через команду:
                celery -A download worker --loglevel=info --pool=solo 
                '''
                print(f"файл копирован в новую папку")
            except IntegrityError:
                session.rollback()
                print("Ошибка: файл с таким именем уже существует")
            finally:
                session.close()

def monitor_folder(folder_path):
    # создать папку если вдруг её нет
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    
    try:
        print(f"Мониторинг запущен для папки: {folder_path}\nНажмите Ctrl+C для остановки")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    folder_to_watch = ".\\files"   # У меня локальная папка
    monitor_folder(folder_to_watch)