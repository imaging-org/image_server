import json
import os.path
import time

import requests
from typing import List
from utils.config import ServerURLS, Endpoints
from utils.constants import Status
from utils.logger import logger


def get_embedding(image_object_key):
    logger.info("Getting Embedding url")
    get_embedding_url = f"{ServerURLS.EMBEDDING_SERVER_URL}{Endpoints.GENERATE_EMBEDDING}"
    body = {
        "image_object_key": image_object_key
    }
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

    if resp.status_code == 200:
        logger.info(f"Received similar image list")
        return resp.json()
    else:
        raise Exception("Error in fetching similar images")


def delete_image_embedding(id_):
    delete_image_embedding_url = f"{ServerURLS.CHROMADB_URL}{Endpoints.DELETE_COLLECTION_BY_ID}/{id_}"
    resp = requests.delete(delete_image_embedding_url)

    if resp.status_code == 200:
        logger.info(f"Deleted image embedding")
    else:
        raise Exception("Error in deleting image embedding")


def reset_chromadb():
    reset_db_url = f"{ServerURLS.CHROMADB_URL}{Endpoints.RESET_DB}"
    resp = requests.get(reset_db_url)

    if resp.status_code == 200:
        logger.info(f"Reset Chromadb successful")
    else:
        raise Exception("Error in Resetting ChromaDB")


def update_saved_image_batch_status(batch_id: str, user_id: str, image_url: str, status: Status, file_path: str = None):
    update_saved_batch_status_url = f"{ServerURLS.MARIADB_SERVER_URL}{Endpoints.UPDATE_SAVE_IMAGE_BATCH_STATUS}"
    body = {
        "batch_id": batch_id,
        "user_id": user_id,
        "image_url": image_url,
        "status": status,
        "completion_timestamp": time.time()
    }

    if file_path is not None:
        body["file_path"] = file_path

    res = requests.post(
        url=update_saved_batch_status_url,
        json=body
    )

    logger.info(f"Updated batch status for batch_id: {batch_id} ; user_id: {user_id} ; Req status: {res.status_code}")


def update_delete_image_batch_status(batch_id: str, user_id: str, image_id: str, status: Status):
    update_delete_batch_status_url = f"{ServerURLS.MARIADB_SERVER_URL}{Endpoints.UPDATE_DELETE_IMAGE_BATCH_STATUS}"
    body = {
        "batch_id": batch_id,
        "user_id": user_id,
        "image_id": image_id,
        "status": status,
        "completion_timestamp": time.time()
    }

    res = requests.post(
        url=update_delete_batch_status_url,
        json=body
    )

    logger.info(f"Updated batch status for batch_id: {batch_id} ; user_id: {user_id} ; Req status: {res.status_code}")


def update_reset_batch_status(batch_id: str, user_id: str, status: Status):
    update_reset_batch_status_url = f"{ServerURLS.MARIADB_SERVER_URL}{Endpoints.UPDATE_RESET_IMAGE_BATCH_STATUS}"
    body = {
        "batch_id": batch_id,
        "user_id": user_id,
        "status": status,
        "completion_timestamp": time.time()
    }

    res = requests.post(
        url=update_reset_batch_status_url,
        json=body
    )

    logger.info(f"Updated batch status for batch_id: {batch_id} ; user_id: {user_id} ; Req status: {res.status_code}")


def update_similar_image_batch_status(batch_id: str, user_id: str, image_id: str, status: Status,
                                      image_id_score_map_list: List[dict] = None):
    update_similar_batch_status_url = f"{ServerURLS.MARIADB_SERVER_URL}{Endpoints.UPDATE_SIMILAR_IMAGE_BATCH_STATUS}"
    body = {
        "batch_id": batch_id,
        "user_id": user_id,
        "image_id": image_id,
        "status": status,
        "completion_timestamp": time.time()
    }

    if image_id_score_map_list is not None:
        body["image_id_score_dict"] = image_id_score_map_list

    res = requests.post(
        url=update_similar_batch_status_url,
        json=body
    )

    logger.info(f"Updated batch status for batch_id: {batch_id} ; user_id: {user_id} ; Req status: {res.status_code}")


def save_error_output_to_file(error):
    output_file_path = os.path.join(os.getcwd(), f"err_output_{int(time.time())}.json")
    with open(output_file_path, "wb") as out_file:
        json.dump(out_file, error)
