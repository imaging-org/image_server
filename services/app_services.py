import json
import os.path
import time

import requests
from utils.config import ServerURLS, Endpoints


def check_health_all_service():
    embedding_server_health_url = f"{ServerURLS.EMBEDDING_SERVER_URL}{Endpoints.HEALTH_CHECK}"
    chromadb_server_health_url = f"{ServerURLS.CHROMADB_URL}{Endpoints.HEALTH_CHECK}"

    try:
        resp_embedding_server = requests.get(embedding_server_health_url)
    except ConnectionError:
        print("Embedding server is DOWN")
    else:
        if resp_embedding_server.status_code == 200:
            print("Embedding server is UP")
        else:
            print("Embedding Server is DOWN")

    try:
        resp_chromadb_server = requests.get(chromadb_server_health_url)
    except ConnectionError:
        print("Chromadb server is DOWN")
    else:
        if resp_chromadb_server.status_code == 200:
            print("Chromadb Server is UP")
        else:
            print("Chromadb Server is DOWN")


def get_embedding(image_object_key):
    print("Getting Embedding url")
    get_embedding_url = f"{ServerURLS.EMBEDDING_SERVER_URL}{Endpoints.GENERATE_EMBEDDING}"
    body = {
        "image_object_key": image_object_key
    }
    print(body)
    resp = requests.post(
        url=get_embedding_url,
        json=body
    )
    print(f"Status of get_embedding request : {resp.status_code}")
    return resp.json()


def insert_embedding(embedding, doc, id_):
    print("Inserting Embedding to Chromadb")

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
    print(f"Status of insert_embedding request : {resp.status_code}")


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
