import json
import os.path
import time

import requests
from utils.config import ServerURLS, Endpoints
from utils.constants import Status
from utils.logger import logger


def get_embedding(image_object_key):
    logger.info("Getting Embedding url")
    get_embedding_url = f"{ServerURLS.EMBEDDING_SERVER_URL}{Endpoints.GENERATE_EMBEDDING}"
    body = {
        "image_object_key": image_object_key
    }
    print(body)
    resp = requests.post(
        url=get_embedding_url,
        json=body
    )
    logger.info(f"Status of get_embedding request : {resp.status_code}")
    return resp.json()


def insert_embedding(embedding, doc, id_):
    logger.info("Inserting Embedding to Chromadb")

    insert_embedding_url = f"{ServerURLS.CHROMADB_URL}{Endpoints.ADD_EMBEDDING}"
    body = {
        "documents": doc,
        "id": id_,
        "embeddings": embedding
    }
    resp = requests.post(
        url=insert_embedding_url,
        json=body
    )
    logger.info(f"Status of insert_embedding request : {resp.status_code}")


def get_similar_image_by_embedding(embedding):
    get_similar_image_url = f"{ServerURLS.CHROMADB_URL}{Endpoints.SIMILAR_IMAGE}"

    resp = requests.post(
        url=get_similar_image_url,
        json=embedding
    )

    return resp.json()


def save_error_output_to_file(error):
    output_file_path = os.path.join(os.getcwd(), f"err_output_{int(time.time())}.json")
    with open(output_file_path, "wb") as out_file:
        json.dump(out_file, error)
