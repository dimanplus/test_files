# Настройки для MinIO
MINIO_ENDPOINT = "ваш-адрес.minio.com"
MINIO_ACCESS_KEY = "access-key"
MINIO_SECRET_KEY = "secret-key"
MINIO_BUCKET = "file-storage"

# Настройки для RabbitMQ
RABBITMQ_URL_FILES = "localhost"
RABBITMQ_URL_NOTIFY = "amqp://guest:guest@localhost"
RABBITMQ_QUEUE = "file_notifications"

# Настройки для Redis 
CELERY_BROKER = "redis://redis:6379/0"
CELERY_BACKEND = "redis://redis:6379/1"