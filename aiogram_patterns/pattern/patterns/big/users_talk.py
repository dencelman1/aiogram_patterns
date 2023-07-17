from aiogram.types import Message
from aiogram import Bot, types, Dispatcher
from aiogram.utils import markdown
from typing import List
from datetime import datetime
from ...patterns.medium.poll import Poll

from ....utils import FileUtils, Emoji




class UsersTalk:

    def __init__(cls, bot: Bot, dp: Dispatcher):
        cls.bot = bot
        cls.dp = dp

        cls.talks = {}
        cls.talk_count = 0

        cls.message_poll = Poll(cls.bot, cls.dp).message
        cls.deanon_users = []

        cls.file_types = [types.ContentType.PHOTO, types.ContentType.DOCUMENT]
    

    async def hand_over_message(cls, message: Message):
        
        users_in_talk = await cls.get_users_in_talk()
        user_id = str(message.from_user.id)
        
        if user_id not in users_in_talk:
            await message.answer("Найдите собеседника с помощью команды /new_talk")
            return
        
        talk_id = await cls.get_talk_id_by_user(user_id)
        talk_data = cls.talks[talk_id]

        recipients = [i for i in talk_data["participants"] if i != user_id]

        
        
        message_data = {
            "text": message.text,
            "user_id": user_id,
            "date": str(datetime.now().timestamp()),
        }

        text = await cls.get_right_message(message)

        for recipient_id in recipients:
            
            if message.content_type in cls.file_types:
                file_path = await FileUtils.hand_over(message, to_id=recipient_id, text= text)
                message_data["file_path"] = file_path
                continue
            
            await cls.bot.send_message(chat_id=recipient_id, text= text, parse_mode=types.ParseMode.MARKDOWN_V2)


        talk_data["messages"].append(message_data)


    async def get_right_message(self, message: Message) -> str:
        if message.content_type in self.file_types:
            text = message.caption
        else:
            text = message.text

        text += await self.get_deanon_user_info(message)
        text = markdown.escape_md(text)

        return text
    

    @staticmethod
    async def get_deanon_sign(message: Message) -> str:
        user_id = message.from_user.id
        username = message.from_user.username
        flag_emoji = Emoji.get_country_emoji(message.from_user.language_code)
        fullname = message.from_user.full_name

        user_info = "{fullname} @{username} {flag_emoji} (ID: {user_id})".format(
            fullname=fullname,
            username=username,
            flag_emoji=flag_emoji,
            user_id=user_id,
        )

        return user_info


    async def get_deanon_user_info(self, message: Message) -> str:
        user_id = message.from_user.id

        is_anon = await self.user_is_anon(user_id)
        if is_anon:
            return ''
        
        deanon_sign = await self.get_deanon_sign(message)

        return "\n\n" + deanon_sign



    async def deanon_me(self, message: Message):
        user_id = message.from_user.id

        is_anon = await self.user_is_anon(user_id)

        if not is_anon:
            await message.answer("⚠️ Вы уже и так деанонимны")
            return
            
        self.deanon_users.append({
            "id": message.from_user.id,
            "username": message.from_user.username,
            'full_name': message.from_user.full_name,
            "language_code": message.from_user.language_code,
        })

        deanon_sign = await self.get_deanon_sign(message)

        text = "\n\n".join([
            "✅ Вы были успешно деанонимизированы",
            "У ваших сообщений будет такая подпись:",
            deanon_sign,
        ])

        await message.answer(text)


    async def anon_me(self, message: Message):
        user_id = message.from_user.id

        is_anon = await self.user_is_anon(user_id)

        if is_anon:
            await message.answer("⚠️ Вы уже и так анонимны")    
            return

        await self.anon_by_id(user_id)
        await message.answer("✅ Вы были успешно анонимизированы")


    async def anon_by_id(self, user_id):
        user_id = int(user_id)

        for user_data in self.deanon_users:

            if user_data['id'] == user_id:
                self.deanon_users.remove(user_data)



    async def user_is_anon(self, user_id):
        user_id = int(user_id)

        for user_data in self.deanon_users:

            if user_data['id'] == user_id:
                return False

        return True
    

    async def found_talk_for_user(cls, message: Message):
        user_id = str(message.from_user.id)

        if str(user_id) in cls.message_poll.polls_data:
            await message.answer("*⚠️ Введите кол-во участников комнаты (от 2х)")
            return

        users_in_talk = await cls.get_users_in_talk()
        forbidden_talks = []

        user_in_talk = user_id in users_in_talk
        
        if user_in_talk:
            user_talk_id = await cls.get_talk_id_by_user(user_id)
            
            await cls.remove_user_from_talk(message)
            forbidden_talks.append(user_talk_id)


        talk_id = await cls.found_free_talk(forbidden_talks= forbidden_talks)

        if talk_id:
            await cls.add_user_to_talk(talk_id, user_id)

            text = "Для того, чтобы покинуть разговор - /leave_talk"
            await cls.bot.send_message(chat_id= user_id, text= text)
            
        else:
            await cls.add_talk(user_id)
            

        

    
    async def found_free_talk(cls, forbidden_talks: List[str] = []) -> str:
        ":return: talk_id (str)"

        for talk_id, talk_data in cls.talks.items():

            if talk_id in forbidden_talks:
                continue

            participants_count = len(talk_data['participants'])
            capacity = talk_data['capacity']
            
            if participants_count < capacity:
                return talk_id


    async def remove_user_from_talk(cls, message: Message):
        user_id = str(message.from_user.id)
        talk_id = await cls.get_talk_id_by_user(user_id)

        if not talk_id:
            text = "Вы не состоите в разговоре, для того чтобы создать или вступить в разговор - /new_talk"
            await message.answer(text)
            return

        talk_data = cls.talks[talk_id]

        talk_data['participants'].remove(user_id)

        notif = "Вы вышли из разговора, в том разговоре осталось {count}/{from_} участников"
        notif = notif.format(count = len(talk_data['participants']), from_ = talk_data['capacity'])
        
        if not talk_data['participants']:
            notif = ", ".join([notif, "беседа была расформирована"])
            await cls.remove_talk(talk_id=talk_id)

        await cls.bot.send_message(chat_id= user_id, text= notif)

        for participant_id in talk_data['participants']:
            notif = "Один из собеседников вышел из разговора, осталось {count}/{from_} участников в беседе"
            notif = notif.format(count = len(talk_data['participants']), from_ = talk_data['capacity'])

            await cls.bot.send_message(chat_id= participant_id, text= notif)
        


    async def add_user_to_talk(cls, talk_id: str, user_id: str):
        talk_data = cls.talks[talk_id]

        if user_id in talk_data['participants']:
            return

        talk_data['participants'].append(user_id)
        participants_count = len(talk_data['participants'])
        capacity = talk_data['capacity']

        for participant_id in talk_data['participants']:

            if participant_id == user_id:
                continue
            
            notif = "Присоединился новый участник в ваш в разговор ({}/{})"
            notif = notif.format(participants_count, capacity)

            await cls.bot.send_message(chat_id= participant_id, text= notif)


        notif = "Вы присоединились к разговору ({}/{}), можете общаться"
        notif = notif.format(participants_count, capacity)

        await cls.bot.send_message(chat_id= user_id, text= notif)


    async def get_talk_id_by_user(cls, user_id: str) -> str:
        
        for talk_id, talk_data in cls.talks.items():
            if user_id in talk_data['participants']:
                return talk_id


    async def get_users_in_talk(cls) -> list:
        users = [
            talk_data["participants"] for talk_id, talk_data in cls.talks.items()
        ]

        buffer = []
        [buffer.extend(sublist) for sublist in users]
        
        return buffer
            

    async def remove_talk(cls, talk_id: str = None, user_id: str = None):

        if talk_id:
            del cls.talks[talk_id]
            return

        if user_id:
            
            for talk_id, talk_data in cls.talks.items():
                participants = talk_data["participants"]
                
                if user_id in participants:
                    del cls.talks[talk_id]
            

    async def add_talk(cls, user_id: str) -> str:
        ":return: talk_id of new talk (str)"

        print(cls.message_poll.polls_data)
        print(str(user_id) in cls.message_poll.polls_data)

        if str(user_id) in cls.message_poll.polls_data:
            return

        await cls.message_poll.ask(
            chat_id=str(user_id),
            questions="❔ Сколько участников должно быть в комнате (больше 2)",
            callback= cls.add_talk_callback,
        )

        
    

    async def add_talk_callback(self, message: Message, data):
        user_id = message.from_user.id

        try:
            capacity = int(message.text)

        except ValueError:
            await message.answer("⚠️ Введите именно цифру/число")
            return

        
        if capacity < 2:
            await message.answer("⚠️ Введите от 2х и больше")
            return
        
        talk_index = str(self.talk_count)

        talk_data = {
            "participants": [str(message.from_user.id)],
            "capacity": capacity,
            "messages": [],
        }

        self.talks[talk_index] = talk_data
        self.talk_count += 1

        notif = "Вы создали новую беседу для {} учасников, ожидайте собеседников".format(capacity)
        await self.bot.send_message(chat_id= user_id, text= notif)

        text = "Для того, чтобы покинуть разговор - /leave_talk"
        await self.bot.send_message(chat_id= user_id, text= text)

        return True
