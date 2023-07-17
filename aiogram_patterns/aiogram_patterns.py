from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types

import logging
import os

from .pattern import Pattern
from .callback import Callback

from .panels import Panel




class AiogramPatterns:
    
    def __init__(self, token: str):

        logging.basicConfig(level=logging.INFO)
        
        self.__bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
        self.dp = Dispatcher(self.core, storage=MemoryStorage())

        self.pattern = Pattern(self.__bot, self.dp)
        self.panel = Panel(self.__bot)

        self.callback = Callback(self.__bot, self.dp, self.pattern)
        
        self.__reload_callback_handlers()


    @property
    def core(self) -> Bot:
        """* aiogram.Bot()"""
        return self.__bot
    

    async def add_callbacks(self, callbacks: list):
        for data, func in callbacks:
            await self.callback.add(data, func)

        self.__reload_callback_handlers()


    def __reload_callback_handlers(self):
        self.dp.register_callback_query_handler(self.callback.callback_handler)


    async def run(self):
        self.print_message("bot start working now")
        await self.dp.start_polling()
        

    def __del__(self):
        self.print_message("bot is taking break")


    def print_message(self, message: str):
        class_name = str(self.__class__.__name__)
        
        text = f"\n[{class_name}]: {message}\n"
        print(text)
        
        return text
    