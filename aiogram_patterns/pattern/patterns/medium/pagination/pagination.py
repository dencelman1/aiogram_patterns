from ....patterns.small.keyboard import Keyboard
from .....utils import FileUtils

from aiogram.types import InlineKeyboardMarkup, CallbackQuery, Message
from typing import Union
from datetime import datetime
import json
import os
from .....config import main_dir




class Pagination:

    def __init__(cls):
        cls.inline = Keyboard().inline
        
        cls.cb_separator = "|"

        test_config = {
            0: "image_1.png",
            1: "image_2.png",
            2: "video_1.mp4",
            3: "fl.txt",
            4: "audio_1.mp3"
        }

        cls.test_data = [
            [
                f"Entry {i}",
                "bro",
                os.path.join(main_dir, "media", test_config[i]) if i in test_config else None,
                f"callback_{i}"
            ]
            for i in range(10)
        ]

        cls.datas = {
            "test": {"data": cls.test_data},
        }


    @property
    def callback_functions(cls) -> dict:
        return {
            "to_page": cls.to_page,
            "entry_view": cls.entry_view,
        }
    

    async def register_data(cls, data_key: str, data: Union[list, dict]):
        cls.datas[data_key] = {"data": data}


    def generate_unikey(cls) -> str:
        now = str(datetime.now().timestamp())
        now = now.replace(".", "")

        return now
        

    async def get_data_key_with_data(cls, data, data_key):
        
        if isinstance(data, str):
            data_key = data
            data = cls.datas[data_key]['data']

        elif data_key is None:
            data_key = cls.generate_unikey()
            await cls.register_data(data_key, data)
        
        elif data is None:
            data = cls.datas[data_key]['data']
        
        return data_key, data


    async def page(
            cls,
            number: int,
            size: int,
            text: str,
            
            titles: list,
            entry_view_titles: list,

            data: Union[list, dict, str] = None,
            data_key: str = None,
            
            extra_catalog_buttons:list = [],
            extra_entry_buttons:list = [],
            back_title:str = "⬅️ Back",

            include_entry_media:bool = False,
            
        ) -> InlineKeyboardMarkup:

        data_key, data = await cls.get_data_key_with_data(data, data_key)

        cls.json_print(data_key)

        size = await cls.correct_size(size)
        pages = await cls.define_pages_amount(data, size)
        number = await cls.correct_current_page(number, pages)

        page_entries = await cls.__get_page_entries(number, size, data, titles, data_key)

        control_buttons_payload = [
            number, pages, size, titles,
            data_key, text,
            entry_view_titles,
            extra_catalog_buttons, extra_entry_buttons,
            back_title, include_entry_media,
        ]
        control_buttons = await cls.__control_buttons(*control_buttons_payload)

        page_keyboard = await cls.inline.create([
            *page_entries,
            control_buttons,
            *extra_catalog_buttons,
        ])

        return page_keyboard


    def get_entry_data(cls, key, data):
        if isinstance(data, dict):
            return data[key]
        
        if isinstance(key, (dict, list)):
            return key

        
    async def __get_prepared_entries(
            cls,
            page_data: Union[list, dict],
            titles,
            data_key: str,
        ) -> list:

        prepared_data = []

        for key in page_data:
            
            entry = cls.get_entry_data(key, page_data)
            
            title_list = [
                cls.get_entry_view_title_value(entry, title)
                for title in titles
            ]
            title_text = "".join(title_list)
            
            if isinstance(entry, list):
                custom_data = entry[-1]

            elif isinstance(entry, dict):
                custom_data = entry["callback_data"]
            

            sep = cls.cb_separator
            callback_data = sep.join(["entry_view", data_key, custom_data])
            prepared_data.append([title_text, callback_data])

        return prepared_data


    def json_print(cls, data):
        if isinstance(data, str):
            print(data)

        else:
            print(json.dumps(data, indent=4))


    @staticmethod
    async def select_page_entries(data, number: int, size: int):
        start_index = (number - 1) * size
        end_index = start_index + size
        slicing = slice(start_index, end_index)

        if isinstance(data, dict):
            entry_keys = list(data.keys())[slicing]

            return {key: data[key] for key in entry_keys}

        return data[slicing]
    

    async def __get_page_entries(
            cls,
            number,
            size,
            data: Union[list, dict],
            titles: Union[int, str, list],
            data_key: str,
        ) -> list:

        page_data = await cls.select_page_entries(data, number, size)

        return await cls.__get_prepared_entries(page_data, titles, data_key)
    

    def define_callback_key(cls, data):
        if isinstance(data, dict):
            return "callback_data"
        
        first_element = data[0]
        
        if isinstance(first_element, dict):
            return "callback_data"
        
        elif isinstance(first_element, list):
            return -1


    async def get_chosen_entry_data(cls, data, custom_callback) -> Union[list, dict]:
        
        callback_key = cls.define_callback_key(data)
        
        for key in data:

            if isinstance(key, str):
                entry_data = data[key]
            
            elif isinstance(key, (list, dict)):
                entry_data = key
            
            if entry_data[callback_key] == custom_callback:
                return entry_data

    
    async def get_entry_media_path(self, data):
        print("data = {}".format(data))

        if isinstance(data, list):
            media_path = data[-2]
        
        elif isinstance(data, dict):
            try:
                media_path = data['media_path']

            except KeyError:
                return

        if not isinstance(media_path, str):
            return
        
        is_correct_file_path = os.path.isfile(media_path) and os.path.exists(media_path)
        if is_correct_file_path:
            return media_path
        
        
    

    def get_entry_view_title_value(cls, data, title: Union[str, int]) -> str:
        
        print(title)
        print(data)

        if isinstance(title, int):
            return str(data[title])
            
        if title.startswith("text="):
            return title.replace("text=", "", 1)
    
        return str(data[title])


    async def entry_view(cls, cb_query: CallbackQuery):
        sep = cls.cb_separator
        _, data_key, custom_callback =  cb_query.data.split(sep)
        
        key_data = cls.datas[data_key]
        entry_view_titles = key_data['entry_view_titles']

        back_title = key_data['back_title']
        back_callback = sep.join(["to_page", data_key, "current"])

        extra_entry_buttons = key_data['extra_entry_buttons']
        
        data = key_data['data']
        
        chosen_entry_data = await cls.get_chosen_entry_data(data, custom_callback)
        
        text = ""
        for title in entry_view_titles:
            text += cls.get_entry_view_title_value(chosen_entry_data, title)

        kb = await Keyboard().inline.create([
            *extra_entry_buttons,
            [back_title, back_callback]
        ])

        include_entry_media = key_data['include_entry_media']
        print("include_entry_media = {}".format(include_entry_media))

        if not include_entry_media:
            return {"text": text, "kb": kb}

        media_path = await cls.get_entry_media_path(chosen_entry_data)
        print("media_path = {}".format(media_path))

        if media_path is None:
            return {"text": text, "kb": kb}

        await cb_query.message.delete()
        
        payload = {
            "chat_id": cb_query.message.chat.id,
            "bot": cb_query.bot,
            "file_path": media_path,
            "text": text,
            "kb": kb,
        }

        response = await FileUtils.send_file(**payload)
        print("response = {}".format(response))
        

    @staticmethod
    async def correct_size(size: int) -> int:
        if size <= 0:
            return 1
        
        return size


    @staticmethod
    async def correct_current_page(number: int, pages: int) -> int:
        if number <= 0:
            return 1
        
        if number > pages:
            return pages
        
        return number


    @staticmethod
    async def define_pages_amount(data: Union[list, dict], size: int) -> int:

        entries = len(data)
        pages = entries // size

        if entries % size and entries >= size:
            pages += 1

        if pages == 0:
            return 1

        return pages

    
    async def is_shouldnt_go_to_new_page(cls, command, start, pred, last) -> bool:
        current = pred + 1

        if command in ["next", "last"] and current == last:
            return True
        
        if command in ["start", "pred"] and current == start:
            return True

        return False


        


    async def to_page(cls, cb_query: CallbackQuery):
        cb_data = cb_query.data
        
        _, data_key, command = cb_data.split(cls.cb_separator)
        
        data = cls.datas[data_key]
        pred = data["pred_page"]
        last = data["last_page"]
        start = 1
        next = data["next_page"]

        titles = data['titles']
        size = data['size']
        current = pred + 1

        extra_payload = {
            "extra_catalog_buttons": data['extra_catalog_buttons'],
            "extra_entry_buttons": data['extra_entry_buttons'],
            "back_title": data['back_title'],
            "include_entry_media": data["include_entry_media"]
        }

        shouldnt_go_to_new_page = await cls.is_shouldnt_go_to_new_page(command, start, pred, last)
        if shouldnt_go_to_new_page:
            return
        
        to_page_dict = {
            "start": start,
            "pred": pred,
            "current": current,
            "next": next,
            "last": last,
        }

        current = to_page_dict[command]
        
        kb = await cls.page(
            number= current,
            size= size,
            data=data_key,
            text= data['text'],
            titles= titles,
            entry_view_titles= data['entry_view_titles'],
            **extra_payload,
        )

        message = cb_query.message
        have_media = await cls.message_have_media(message)
        if have_media:
            await message.delete()
            await cb_query.bot.send_message(chat_id=message.chat.id,
                                            text=data['text'],
                                            reply_markup=kb)

            return


        return {"kb": kb, "text": data['text']}


    async def message_have_media(self, message: Message) -> bool:
        medias = [
            "photo", "video",
            "audio", "voice",
            "document", "sticker",
            "animation", "contact",
            "location",
        ]

        bool_value = False
        for media in medias:
            bool_value = bool_value or bool(getattr(message, media))

        return bool_value



    async def __control_buttons(
            cls,
            number: int,
            pages: int,
            size: int,
            titles,
            data_key: str,
            text: str,
            entry_view_titles: list,

            extra_catalog_buttons: list,
            extra_entry_buttons: list,
            back_title:str,

            include_entry_media:bool,
            
        ) -> str:

        start_page = 1
        pred_page = number - 1
        next_page = number + 1
        last_page = pages

        saved_data = {
            "data": cls.datas[data_key]['data'],
            "text": text,

            "titles": titles,
            
            "extra_catalog_buttons": extra_catalog_buttons,
            "extra_entry_buttons": extra_entry_buttons,
            "back_title": back_title,
            "include_entry_media": include_entry_media,
            
            "size": size,

            "entry_view_titles": entry_view_titles,

            "start_page": start_page,
            "pred_page": pred_page,
            "next_page": next_page,
            "last_page": last_page,
        }
        cls.datas[data_key] = saved_data

        callback_data = ["to_page", data_key]

        sep = cls.cb_separator

        def callback_to(command: str) -> str:
            return sep.join([ *callback_data, command ])
            
        buttons = [
            ["◀️◀️", callback_to("start")],
            ["◀️", callback_to("pred")],
            [f"{number} / {pages}"],
            ["▶️", callback_to("next")],
            ["▶️▶️", callback_to("last")],
        ]

        return buttons
    