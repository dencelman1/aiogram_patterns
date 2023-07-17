from aiogram import Bot, Dispatcher
from .callback_core import CallbackCore

from ..pattern import Pattern






class Callback(CallbackCore):

    def __init__(cls, bot: Bot, dp: Dispatcher, pattern: Pattern):
        super().__init__(bot, dp)

        cls.pattern = pattern
        
        cls.other_cb_functions = {}


    async def add(cls, data: str, func):

        if data in cls.other_cb_functions:
            error = "choose other data for your callback (it's already taken)"
            raise Exception(error)

        cls.other_cb_functions[data] = func

    
    async def all_cb_functions(cls) -> dict:
        cb_functions = await cls.pattern_callback_functions()
        cb_functions.update(cls.other_cb_functions)

        return cb_functions
    
    
    async def get_pattern_object(cls, pattern_type:str, pattern_name: str):
        pattern_type_object = getattr(cls.pattern, pattern_type)

        return getattr(pattern_type_object, pattern_name)
            

    async def get_pattern_callback_functions(cls, pattern_type:str, pattern_name: str) -> dict:
        pattern_obj = await cls.get_pattern_object(pattern_type, pattern_name)

        return pattern_obj.callback_functions
    

    async def load_pattern_callback_functions():
        pass
    

    async def pattern_callback_functions(cls) -> dict:
        cb_functions = {}

        pattern_types = Pattern.PATTERN_NAMES_WITH_CALLBACKS
        
        for pattern_type, pattern_names in pattern_types.items():

            for pattern_name in pattern_names:
                pattern_functions = await cls.get_pattern_callback_functions(pattern_type, pattern_name)
                cb_functions.update(pattern_functions)
        
        return cb_functions
    