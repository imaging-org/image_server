from dataclasses import dataclass
from os import getenv


@dataclass
class RabbitMQConfig:
    RABBIT_MQ_HOST = getenv("RABBIT_MQ_HOST", "localhost")
    QUEUE_NAME = getenv("QUEUE_NAME", "image_service_queue")


@dataclass
class MinioConfig:
    ACCESS_KEY = getenv("ACCESS_KEY", "qLU7Yb5jfyXmHQhUyRb5")
    SECRET_KEY = getenv("SECRET_KEY", "FEAVIoGFuY179WzrGkYhj9swt3IMjCqb8cwFP5db")
    BUCKET_NAME = getenv("BUCKET_NAME", "test-bucket")


@dataclass
class ServerURLS:
    CHROMADB_URL = getenv("CHROMADB_URL", "http://localhost:5646")
    EMBEDDING_SERVER_URL = getenv("EMBEDDING_SERVER_URL", "http://localhost:5545")


@dataclass
class Endpoints:
    HEALTH_CHECK = "/health_check"
    GENERATE_EMBEDDING = "/generate_embedding"
    ADD_EMBEDDING = "/add_embedding"
    SIMILAR_IMAGE = "/get_similar_image"
    DELETE_COLLECTION_BY_ID = "/delete_id_from_coll"
    RESET_DB = "/reset_db"
