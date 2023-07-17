from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram import Bot, Dispatcher

from typing import Union




class MessagePoll:

    class Answers(StatesGroup):
        response = State()

    def __init__(cls, dp: Dispatcher, bot: Bot):
        cls.bot = bot
        cls.dp = dp

        cls.polls_data = {}


    @property
    def all_polls_count(cls):
        return len(cls.polls_data)


    async def ask(cls, chat_id: str, questions: Union[str, list], callback = None) -> str:
        chat_id = str(chat_id)

        cls.reset(chat_id, callback)

        if isinstance(questions, str):
            questions = [questions]

        poll = cls.get_poll(chat_id)
        poll["asked_count"] = len(questions)
        
        await cls.save_questions(chat_id, questions)
        await cls.bot.send_message(int(chat_id), questions[0])

        cls.dp.register_message_handler(cls.to_callback, state=cls.Answers.response)
        await cls.Answers.response.set()
        


    def reset(cls, user_id: str, callback):
        input_data = {
            "asked_count": 0,
            "processed_count": 0,
            "poll_result": {},
            "callback": callback,
        }
        cls.polls_data[str(user_id)] = {**input_data}



    async def test_callback(cls, message: Message, poll_result: dict):
        await message.answer(f"{poll_result}")


    async def to_callback(cls, message: Message, state: FSMContext):
        chat_id = str(message.from_user.id)
        answer = message.text

        current_question = await cls.define_current_question(chat_id)

        await cls.save_answer(chat_id, current_question, answer)

        processed_count = cls.get_processed_count(chat_id)
        asked_count = cls.get_asked_count(chat_id)
        poll_result = cls.get_poll_result(chat_id)
        
        if processed_count >= asked_count:
            callback = cls.get_callback(chat_id)
            result = await callback(message, poll_result)

            if result is None:
                poll = cls.get_poll(chat_id)

                poll["processed_count"] -= 1
                poll['poll_result'][current_question] = None

                return

            await cls.remove_poll(state, chat_id)
            return
        
        current_question = await cls.define_current_question(chat_id)
        await message.answer(current_question)

        cls.dp.register_message_handler(cls.to_callback, state=cls.Answers.response)
        await cls.Answers.response.set()
    

    async def remove_poll(cls, state: FSMContext, user_id: str) -> None:
        await state.finish()
        del cls.polls_data[user_id]

    def get_poll(cls, chat_id) -> dict:
        return cls.polls_data[chat_id]
    
    async def save_single_dialog(cls, chat_id: str, question, answer):
        poll_result = cls.get_poll_result(chat_id)
        poll_result[question] = answer



    async def save_questions(cls, chat_id: str, questions: list):
        asked_count = cls.get_asked_count(chat_id)
        
        for question_index in range(asked_count):
            question = questions[question_index]
            await cls.save_question(chat_id, question)


    async def save_question(cls, chat_id: str, question):
        await cls.save_single_dialog(chat_id, question=question, answer=None)

    async def save_answer(cls, chat_id: str, question, answer):
        await cls.save_single_dialog(chat_id, question=question, answer=answer)

        cls.get_poll(chat_id)["processed_count"] += 1


    def get_processed_count(cls, chat_id) -> int:
        return cls.get_poll(chat_id)['processed_count']
    
    def get_asked_count(cls, chat_id) -> int:
        return cls.get_poll(chat_id)['asked_count']
    
    def get_poll_result(cls, chat_id) -> dict:
        return cls.get_poll(chat_id)["poll_result"]
    
    def get_callback(cls, chat_id):
        return cls.get_poll(chat_id)['callback']
    

    async def define_current_question(cls, chat_id: str) -> str:
        current_index = cls.get_processed_count(chat_id)
        questions = list(cls.get_poll_result(chat_id))
        current_question = questions[current_index]

        return current_question
        