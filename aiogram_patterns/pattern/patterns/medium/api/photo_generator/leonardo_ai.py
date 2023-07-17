from aiogram.types import File, PhotoSize, Message
from ......config import main_dir

from typing import Literal
import urllib.request
from datetime import datetime as d
from os.path import join
from requests.models import Response

import asyncio
import json
import requests




class LeonardoAI:
    
    models = {
        "creative": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",
        "select": "cd2b2a15-9760-4174-a5ff-4d2925057376",
        "signature": "291be633-cb24-434f-898f-e662799936ad",
    }
    

    def __init__(self, api_key:str, account_id:str):
        self.api_url = "https://cloud.leonardo.ai/api/rest/v1/models"
        self.api_key = api_key
        self.account_id = account_id

        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }


    def get_model_id(
            self,
            model_name: Literal["creative", "select", "signature"] = "creative"
        ):
        return self.models.get(model_name)
        


    async def get_answer(self, prompt: str, negative_prompt = None, init_image_id = None) -> list:
        
        generation_id = await self.generate_photo(
            prompt,
            negative_prompt= negative_prompt,
            init_image_id = init_image_id,
        )
        global_pathes = await self.get_global_pathes_from_id(generation_id)
        local_pathes = await self.download_photos(global_pathes)

        return local_pathes
        

    async def download_photos(self, global_pathes: list):
        local_pathes = [ self.download_photo(global_path) for global_path in global_pathes ]

        return local_pathes



    def generate_filename(self, file_extension: str):
        filename = str(d.now().timestamp()).replace(".", "")
        
        return ".".join([filename, file_extension])


    def download_photo(self, url: str) -> str:
        file_extension = url.split(".")[-1]
        filename = self.generate_filename(file_extension)
        
        file_path = join(main_dir, f"api_media/{filename}")
        urllib.request.urlretrieve(url, file_path)
        
        return filename


    async def get_global_pathes_from_id(self, generation_id: str) -> list:

        await asyncio.sleep(11)
        
        url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
        headers = {
            "accept": "application/json",
            "authorization": "Bearer 5fec2650-8bd9-4d38-ae48-5668a2bfa03b"
        }

        response = requests.get(url, headers=headers)
        
        response = response.json()
        
        generated_images = response["generations_by_pk"]["generated_images"]

        global_pathes = [
            image_obj["url"] for image_obj in generated_images
        ]
        
        return global_pathes
    

    async def generate_photo(
            self,
            prompt: str,
            width = 512,
            height = 512,
            negative_prompt = None,
            
            init_image_id: str = None,
            init_strength: float = 0.4,
        ) -> list:
        
        prompt = f"{prompt}"
        
        payload = {
            "prompt": prompt,
            "modelId": self.get_model_id("creative"),
            "width": width,
            "height": height,
        }

        print(f"init_image_id = {init_image_id}")

        if init_image_id is not None:
            payload["init_image_id"] = str(init_image_id)
            payload['init_strength'] = init_strength

        if negative_prompt is not None:
            payload['negative_prompt'] = negative_prompt
        
        url = "https://cloud.leonardo.ai/api/rest/v1/generations"
        response = requests.post(url, json=payload, headers=self.headers)
        response = response.json()

        print("\n\npayload: ")
        print(json.dumps(payload, indent= 4))

        print("\n\nresponse: ")
        print(json.dumps(response, indent= 4))

        # {
        #     "sdGenerationJob": {
        #         "generationId": "491cc493-71d3-4e87-bd50-fb613139ffca"
        #     }
        # }
        
        generation_job = response["sdGenerationJob"]
        generating_id = generation_job["generationId"]

        return generating_id



    async def get_dataset_image(self, file_extension: str) -> Response:
        url = "https://cloud.leonardo.ai/api/rest/v1/init-image"

        payload = {"extension": file_extension}
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(url, json=payload, headers=headers)
        await asyncio.sleep(11)

        return response
        

    async def download_photo_from_telegram(self, message: Message):
        if message.document:
            photo: File = await message.document.get_file()
        
        elif message.photo:
            photo: PhotoSize = message.photo[0]
        
        file_id = photo.file_id
        photo_file = await message.bot.get_file(file_id)
        file_extension = photo_file.file_path.split('.')[-1]

        filename = self.generate_filename(file_extension)
        file_path = join(main_dir, f"api_media/{filename}")
        
        await photo.download(destination_file= file_path)

        return file_path


    async def upload_dataset_image(self, file_path: str) -> str:
        ":return: init image id (str)"

        file_extension = file_path.split(".")[-1]

        response = await self.get_dataset_image(file_extension)
        
        print(json.dumps(response.json(), indent= 4))

        image_data = response.json()['uploadInitImage']

        image_id = image_data['id']
        fields = json.loads(image_data['fields'])
        url = image_data['url']
        files = {'file': open(file_path, 'rb')}
        
        await asyncio.sleep(11)

        response = requests.post(url, data=fields, files=files)
        
        return image_id
    