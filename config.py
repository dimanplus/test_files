# Настройки для MinIO
MINIO_ENDPOINT = "ваш-адрес.minio.com"
MINIO_ACCESS_KEY = "access-key"
MINIO_SECRET_KEY = "secret-key"
MINIO_BUCKET = "file-storage"

# Настройки для RabbitMQ
RABBITMQ_URL_FILES = "localhost"
RABBITMQ_URL_NOTIFY = "amqp://guest:guest@localhost"
RABBITMQ_QUEUE = "file_notifications"

# Тут должны быть настройки для Redis (но у мебя все через RabbitMQ)
CELERY_BROKER = "amqp://guest:guest@localhost"
CELERY_BACKEND = "rpc://"