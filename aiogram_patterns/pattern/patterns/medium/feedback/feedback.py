from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery, Message

from ....patterns.small.keyboard import Keyboard
from ....patterns.medium.poll import Poll

from .feedback_utils import FeedbackUtils



class Feedback(FeedbackUtils):

    def __init__(cls, bot: Bot, dp: Dispatcher):
        super().__init__(bot, dp)

        cls.questions = {}
        cls.processed_count = 0
        
        cls.text_to_users = ["🗣 Задайте свой вопрос администраторам:"]
        cls.text_to_admins = ["🗣 Напишите ваш ответ пользователю:"]

        cls.poll = Poll(bot, dp)
        cls.inline = Keyboard().inline

        cls.admins = [1169333593, 5123713841]


    @property
    def callback_functions(cls) -> dict:
        functions = {
            "asking_for_feedback": cls.asking_for_feedback,
            "answering_for_feedback": cls.answering_for_feedback,
        }

        return functions
    

    async def asking_for_feedback(cls, cb_query: CallbackQuery):
        user_id = cb_query.from_user.id
        
        async def current_callback(message, data):
            await cls.callback_of_asking(message, user_id, data)

        await cls.poll.message.ask(
            chat_id= user_id,
            questions= cls.text_to_users,
            callback= current_callback,
        )
    

    
    

    async def callback_of_asking(cls, message: Message, user_id, data: dict):
        question_to_admin = data[cls.text_to_users[0]]

        await cls.add_question(user_id, question_to_admin)
        question_id = await cls.get_question_id_by_text(user_id, question_to_admin)
        
        keyboard_for_admin = await cls.get_answer_keyboard(question_id)

        question_text = await cls.get_request_text_to_admins(message, question_to_admin)
        await cls.send_to_admins(text=question_text, reply_markup=keyboard_for_admin)
        

    async def answering_for_feedback(cls, cb_query: CallbackQuery):
        admin_id = cb_query.from_user.id
        question_id = cb_query.data.split("|")[-1]

        user_id = await cls.get_user_id_from_question_id(question_id)
        user_id = str(user_id)

        if user_id not in cls.questions:
            await cb_query.answer("На это сообщение пользователя уже ответили")
            return

        async def current_callback(message, data):
            await cls.callback_of_answering(message, question_id, data)

        await cls.poll.message.ask(
            chat_id= admin_id,
            questions= cls.text_to_admins,
            callback= current_callback,
        )


    async def callback_of_answering(cls, message: Message, question_id, data: dict):
        answer_from_admin = data[cls.text_to_admins[0]]
        question_id = int(question_id)
        
        user_id = await cls.get_user_id_from_question_id(question_id)
        to_admins_notify = await cls.get_answering_notify_text(message, question_id, answer_from_admin)

        await cls.answer(user_id, question_id, answer_from_admin)
        await cls.send_to_admins(text=to_admins_notify, reply_markup=None)


    async def answer(cls, user_id, question_id: int, text: str):
        user_id = str(user_id)

        answer_text = await cls.get_answer_text(question_id, text)

        await cls.remove_question_if_exists(user_id, question_id)
        await cls.bot.send_message(chat_id=user_id, text=answer_text)


    async def add_question(cls, user_id, question: str):
        user_id = str(user_id)
        await cls.register_user_if_not_exists(user_id)

        await cls.set_question(user_id, question)


    
                

    


    
