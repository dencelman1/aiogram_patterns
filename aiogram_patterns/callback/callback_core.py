from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from inspect import iscoroutinefunction




class CallbackCore:

    def __init__(cls, bot: Bot, dp: Dispatcher):
        cls.bot = bot
        cls.dp = dp


    async def __process_callback(cls, func, *args):
        args = list(args)

        if iscoroutinefunction(func):
            return await func(*args)

        return func(*args)


    async def __define_callback_function(cls, cb_query: CallbackQuery):
        

        cb_data = cb_query.data
        
        all_cb_functions = await cls.all_cb_functions()

        for key in all_cb_functions:

            if key in cb_data:
                func = all_cb_functions[key]

                return await cls.__process_callback(func, cb_query)

    
    async def callback_handler(cls, cb_query: CallbackQuery):
        
        callback_answer = await cls.__define_callback_function(cb_query)

        if not callback_answer:
            return

        text = callback_answer['text']
        kb = callback_answer['kb']
        
        try:
            await cls.bot.edit_message_text(
                chat_id=cb_query.message.chat.id,
                message_id=cb_query.message.message_id,
                text=text,
                reply_markup=kb,
            )

        except:
            await cls.bot.send_message(
                chat_id=cb_query.message.chat.id,
                text=text,
                reply_markup=kb,
            )
