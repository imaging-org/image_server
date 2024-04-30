import json

from flask import Flask, Response, request
from flask_cors import CORS

from services.download_service import DownloadService
from services.minio_service import MinioService
from services.app_services import (check_health_all_service, get_embedding, insert_embedding,
                                   get_similar_image_by_embedding, save_error_output_to_file)

from utils.config import ServerURLS
from utils.config import Endpoints

import requests

app = Flask(__name__)
CORS(app)
check_health_all_service()

minio_service = MinioService()


@app.get("/health_check")
def health_check():
    return Response(
        status=200,
        response=json.dumps({
            "status": "ok"
        })
    )


@app.post("/save_image")
def save_image():
    try:
        print("Hit route : /save_image")
        image_url = request.json.get("image_url")
        download_service = DownloadService()
        download_service.download_image(image_url)
        try:
            minio_service.put_file(download_service.temp_file_path, download_service.temp_image_name)
            embedding = get_embedding(download_service.temp_image_name)
            insert_embedding(embedding, download_service.temp_image_name, download_service.file_id)
        except Exception as e:
            print(f"Error in saving image : {e}")
        finally:
            download_service.delete_image()

        return Response(status=200,
                        response=json.dumps({
                            "status": "saved image"
                        }))
    except Exception as e:
        print(f"Error in saving image : {e}")
        return Response(status=500,
                        response=json.dumps({
                            "status": "Error in saving image",
                            "error": str(e)
                        }))


@app.delete("/delete_image_by_id/<id>")
def delete_image_by_id(id_):
    try:
        delete_embedding_url = f"{ServerURLS.CHROMADB_URL}{Endpoints.DELETE_COLLECTION_BY_ID}/{id_}"
        resp = requests.delete(delete_embedding_url)
        print(f"Deleted image embedding by id status : {resp.status_code}")

        minio_service.delete_file(f"temp_image_{id_}.png")
        print(f"Deleted image from minio")

        return Response(status=200,
                        response=json.dumps({
                            "status": "deleted image"
                        }))
    except Exception as e:
        print(f"Error in deleting image : {e}")
        return Response(status=500,
                        response=json.dumps({
                            "status": "Error in deleting image",
                            "error": str(e)
                        }))


@app.post("/get_similar_image")
def get_similar_image():
    try:
        image_url = request.json.get("image_url")

        download_service = DownloadService()
        download_service.download_image(image_url)

        minio_service.put_file(download_service.temp_file_path, download_service.temp_image_name)

        embedding = get_embedding(download_service.temp_image_name)

        resp = get_similar_image_by_embedding(embedding)

        return Response(status=200,
                        response=json.dumps({
                            "similar_image": resp
                        }))
    except Exception as e:
        # print(f"Error in fetching similar image : {e}")
        save_error_output_to_file(e)
        return Response(status=500,
                        response=json.dumps({
                            "status": "Error in fetching similar image",
                            "error": str(e)
                        }))


@app.get("/reset_db_and_minio")
def reset_db_and_minio():
    try:
        status = minio_service.reset_bucket()
        reset_db_url = f"{ServerURLS.CHROMADB_URL}{Endpoints.RESET_DB}"
        resp = requests.get(reset_db_url)

        return Response(status=200,
                        response=json.dumps({
                            "reset_db": resp.json().get("status"),
                            "reset_minio": status
                        }))

    except Exception as e:
        print(f"Error in resetting DB : {e}")
        return Response(status=500,
                        response=json.dumps({
                            "status": "Error in resetting DB",
                            "error": str(e)
                        }))


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=4747)
