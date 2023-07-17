from datetime import datetime as d
from aiogram import types, Bot
from aiogram.types import File, PhotoSize, Message
from aiogram.utils.exceptions import BadRequest
import os
from ..config import main_dir
import mimetypes




class FileUtils:

    TELEGRAM_FILE_TYPES = {
        "document": ['application', "message", "text"],
        'voice': ['audio'],
        'photo': ['image'],
        'video': ['video'],
    }

    @staticmethod
    def all_file_types() -> list:
        telegram_types = FileUtils.TELEGRAM_FILE_TYPES.items()
        types = []
        for _, file_types in telegram_types:
            types.extend(file_types)

        return types
        
    

    @staticmethod
    async def send_file(bot: Bot, chat_id:int, file_path:str, text:str, kb):
        file_type:str = await FileUtils.define_telegram_file_type(file_path)
        method = "send" + file_type.capitalize()

        message_payload = {
            'chat_id': chat_id,
            "text": text,
            'reply_markup': kb,
        }

        with open(file_path, 'rb') as file:
            payload = {
                "file_type": file_type,
                "method": method,
                "file": file,
                "payload": message_payload,
            }

            if file_type in ["photo", "voice"]:
                message_payload["caption"] = message_payload.pop("text")
                message_payload[file_type] = file

                send_function = getattr(bot, f"send_{file_type}")
                return await send_function(**message_payload)
                
            return await bot.send_file(**payload)


    @staticmethod
    async def define_telegram_file_type(file_path:str) -> str:
        file_type = FileUtils.define_file_type(file_path)
        telegram_types = FileUtils.TELEGRAM_FILE_TYPES
        for telegram_type, types in telegram_types.items():
            if file_type in types:
                return telegram_type
        
        return "document"


    @staticmethod
    async def define_file_type(file_path) -> str:
        _, file_extension = os.path.splitext(file_path)
        
        for extension, mime_type in mimetypes.types_map.items():
            if file_extension in extension:
                return mime_type.split('/')[0].lower()
        
        return "text"
            


    @staticmethod
    def generate_filename(file_format: str) -> str:
        now = d.now().timestamp()
        
        return str(now).replace(".", "") + f".{file_format}"


    @staticmethod
    async def hand_over(message: Message, to_id, text = None):
        """:return: file_path"""

        bot = message.bot

        file_path = await FileUtils.download(message)
        
        payload = {
            "bot": bot,
            "chat_id": to_id,
            "file_path": file_path,
            "text": text,
        }

        await FileUtils.send(**payload)

        return file_path


    @staticmethod
    async def download(message: types.Message):
        """:return: path of downloaded file"""

        bot = message.bot
        
        if message.document:
            filename = message.document.file_name
            photo: File = await message.document.get_file()
            
        elif message.photo:
            filename = "photo.png"
            photo: PhotoSize = message.photo[-1]
        
        file_path = await FileUtils.set_file_path(filename)
        await bot.download_file_by_id(file_id=photo.file_id, destination=file_path)

        return file_path
    

    @staticmethod
    async def set_file_path(filename:str):
        file_extension = os.path.splitext(filename)[-1]
        filename = FileUtils.generate_filename(file_extension)

        file_path = os.path.join(main_dir, f"media/{filename}")

        return file_path


    @staticmethod
    async def send(bot: Bot, chat_id, file_path:str, text:str = None) -> str:
        
        file = lambda: open(file_path, 'rb')

        payload = {
            "chat_id": chat_id,
            "caption": text,
            "parse_mode": types.ParseMode.MARKDOWN_V2,
        }
        
        try:
            await bot.send_photo(photo= file(), **payload)
            
        except BadRequest:
            await bot.send_document(document= file(), **payload)
