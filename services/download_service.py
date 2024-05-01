import shutil
import uuid

import requests
import os

from utils.logger import logger


class DownloadService:
    def __init__(self):
        self.file_id = str(uuid.uuid4())
        self.temp_image_name = f"temp_image_{self.file_id}.png"
        self._temp_dir_path = os.path.join(os.getcwd(), "temp")

        try:
            os.makedirs(self._temp_dir_path)
        except FileExistsError:
            pass

        self.temp_file_path = os.path.join(self._temp_dir_path, self.temp_image_name)

    def download_image(self, url):
        logger.info(f"Downloading image and saving as file : {self.temp_file_path}")

        resp = requests.get(url, stream=True)
        with open(self.temp_file_path, "wb") as out_file:
            shutil.copyfileobj(resp.raw, out_file)
        del resp

    def delete_image(self):
        os.remove(self.temp_file_path)
