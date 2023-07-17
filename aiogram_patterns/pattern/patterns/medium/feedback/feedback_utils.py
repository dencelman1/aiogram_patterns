from aiogram import Bot, Dispatcher
from aiogram.types import Message
from typing import Union





class FeedbackUtils:

    def __init__(cls, bot: Bot, dp: Dispatcher):
        cls.bot = bot
        cls.dp = dp


    async def get_answering_notify_text(cls, message: Message, question_id, answer) -> str:
        user_id = await cls.get_user_id_from_question_id(question_id)

        user_chat = await cls.bot.get_chat(user_id)
        user_name = user_chat.username

        question_text = await cls.get_question_text_by_id(question_id)

        admin_username = message.from_user.username
        admin_id = message.from_user.id

        to_admins_notify = f"✅⚠️ Администратор @{admin_username} (ID: {admin_id}) "
        to_admins_notify += f"пользователю @{user_name} (ID {user_id})\n▶️ на вопрос:\n\n"
        to_admins_notify += f"{question_text}\n\n👉 ответил:\n\n"
        to_admins_notify += f"{answer}"

        return to_admins_notify


    async def set_question(cls, user_id: str, question: str) -> int:
        question_id = cls.processed_count

        requests: list = cls.questions[user_id]['requests']
        requests.append({"id": question_id, "text": question})

        cls.processed_count += 1

    
    async def get_user_id_from_question_id(cls, question_id: int) -> str:
        question_id = int(question_id)
        questions = cls.questions

        for user_id in questions:
            requests = await cls.get_user_requests(user_id)

            for question_data in requests:
                current_question_id = question_data['id']
                
                if question_id == current_question_id:
                    return user_id
                
    
    async def get_answer_text(cls, question_id, text) -> str:
        user_id = await cls.get_user_id_from_question_id(question_id)
        question_text = await cls.get_question_text(user_id, question_id)

        answer_text = f"▶️ Вопрос:\n\n{question_text}\n\n"
        answer_text += f"👉 Ответ от администратора:\n\n{text}"

        return answer_text



    async def get_question_text(cls, user_id: str, question_id: int) -> str:
        requests = cls.questions[user_id]['requests']
        question = requests[question_id]
        question_text = question['text']

        return question_text


    async def register_user_if_not_exists(cls, user_id: str):
        if user_id not in cls.questions:
            await cls.reset(user_id)

    


        
    async def remove_question_if_exists(cls, user_id: str, question_id: int):
        requests = await cls.get_user_requests(user_id)
        
        for i in range(len(requests)):
            question_data = requests[i]
            current_question_id = question_data['id']

            if current_question_id == question_id:
                requests.remove(question_data)


    async def reset(cls, user_id):
        cls.questions[user_id] = {"requests": []}


    async def get_user_requests(cls, user_id: str) -> list:
        user_id = str(user_id)

        return cls.questions[user_id]['requests']
        

    async def get_question_id_by_text(cls, user_id, text: str) -> Union[int, None]:
        user_id = str(user_id)
        requests = await cls.get_user_requests(user_id)

        for question_data in requests:
            question_id = question_data['id']
            question_text = question_data['text']

            if question_text == text:
                return question_id
                

    async def get_question_text_by_id(cls, chosen_id: int) -> Union[str, None]:
        questions = cls.questions

        for user_id in questions:
            requests = await cls.get_user_requests(user_id)

            for question_data in requests:
                question_id = question_data['id']
                question_text = question_data['text']

                if question_id == chosen_id:
                    return question_text
    

    async def send_to_admins(cls, text, reply_markup):
        for admin_id in cls.admins:
            await cls.bot.send_message(chat_id=admin_id, text=text, reply_markup=reply_markup)


    async def get_answer_keyboard(cls, question_id: int):
        kb = await cls.inline.create([
            ["📢 Ответить", f'answering_for_feedback|{question_id}']
        ])

        return kb
    

    async def get_feedback_ask_button(cls, button_text: str):
        return [button_text, "asking_for_feedback"]
    

    async def get_request_text_to_admins(cls, message: Message, question: str):
        user_name = message.from_user.username
        user_id = message.from_user.id

        question_text = f"❔ Вопрос от юзера @{user_name} (ID: {user_id}):\n\n{question}\n\n"

        return question_text
    