import json

import pika
import sys
import os

from services.download_service import DownloadService
from services.minio_service import MinioService
from services.app_services import (get_embedding, insert_embedding, delete_image_embedding, reset_chromadb,
                                   get_similar_image_by_embedding, update_saved_image_batch_status,
                                   update_delete_image_batch_status, update_reset_batch_status,
                                   update_similar_image_batch_status)

from model.MQMessage import MQMessage, EventTypeEnum

from utils.config import RabbitMQConfig
from utils.constants import Status
from utils.logger import logger

from typing import List

minio_service = MinioService()


def save_image(batch_id, user_id, image_url):
    download_service = DownloadService()

    try:
        download_service.download_image(image_url)
        minio_service.put_file(download_service.temp_file_path, download_service.temp_image_name)
        embedding = get_embedding(download_service.temp_image_name)
        insert_embedding(embedding, download_service.temp_image_name, download_service.file_id)

    except Exception as e:
        logger.error(f"Error in saving image : {e}")
        update_saved_image_batch_status(batch_id, user_id, image_url, Status.FAILED)
    else:
        logger.info(f"Successfully saved image of url : {image_url}")
        update_saved_image_batch_status(batch_id, user_id, image_url, Status.SUCCESS, download_service.temp_image_name)
    finally:
        download_service.delete_image()


def delete_image_by_id(batch_id: str, user_id: str, image_id: str):
    try:
        delete_image_embedding(image_id)
        minio_service.delete_file(f"temp_image_{image_id}.png")

    except Exception as e:
        logger.error(f"Error in deleting image : {e}")
        update_delete_image_batch_status(batch_id, user_id, image_id, Status.FAILED)
    else:
        logger.info(f"Successfully deleted image of id : {image_id}")
        update_delete_image_batch_status(batch_id, user_id, image_id, Status.SUCCESS)


def get_similar_image(batch_id, user_id, image_id):
    try:
        embedding = get_embedding(f"temp_image_{image_id}.png")
        resp = get_similar_image_by_embedding(embedding)

        id_score_map_list: List[dict] = [{resp["status"]["ids"][0][index]: resp["status"]["distances"][0][index]} for
                                         index, id_ in
                                         enumerate(resp["status"]["ids"][0])]

    except Exception as e:
        logger.error(f"Error in fetching similar images : {e}")
        update_similar_image_batch_status(batch_id, user_id, image_id, Status.FAILED)
    else:
        logger.info(f"Successfully fetched similar images of id : {image_id}")
        update_similar_image_batch_status(batch_id, user_id, image_id, Status.SUCCESS, id_score_map_list)


def reset_db_and_minio(batch_id, user_id):
    try:
        minio_service.reset_bucket()
        reset_chromadb()

    except Exception as e:
        logger.error(f"Error in resetting db and/or minio : {e}")
        update_reset_batch_status(batch_id, user_id, Status.FAILED)
    else:
        logger.info(f"Successfully Reset DB and minio")
        update_reset_batch_status(batch_id, user_id, Status.SUCCESS)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RabbitMQConfig.RABBIT_MQ_HOST))
    channel = connection.channel()

    channel.queue_declare(queue=RabbitMQConfig.QUEUE_NAME)

    def callback(ch, method, properties, body):
        logger.debug(ch)
        logger.debug(method)
        logger.debug(properties)
        logger.debug(f" [x] Received {body}")
        data = json.load(body)
        message = MQMessage.from_json(data)

        if message.EventType.value == EventTypeEnum.SAVE.value:
            save_image(message.batch_id, message.user_id, message.ImageURL)
        elif message.EventType.value == EventTypeEnum.SIMILAR.value:
            get_similar_image(message.batch_id, message.user_id, message.image_id)
        elif message.EventType.value == EventTypeEnum.DELETE.value:
            delete_image_by_id(message.batch_id, message.user_id, message.image_id)
        elif message.EventType.value == EventTypeEnum.RESET.value:
            reset_db_and_minio(message.batch_id, message.user_id)

    channel.basic_consume(queue=RabbitMQConfig.QUEUE_NAME, on_message_callback=callback, auto_ack=True)

    logger.info(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        logger.error('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os.abort()
