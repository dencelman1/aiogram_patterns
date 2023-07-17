from aiogram import Bot, Dispatcher
from aiogram.types import Message, ChatPermissions
from aiogram.utils.exceptions import CantRestrictChatOwner, UserIsAnAdministratorOfTheChat
from datetime import datetime, timedelta




class GroupAdmin:

    def __init__(cls, bot: Bot, dp: Dispatcher):
        cls.bot = bot
        cls.dp = dp

        cls.bad_words = ['fuck', 'сука', 'блять', 'ебать', 'трахать']
        

    async def mute(cls, chat_id: int, user_id: int, time_sec: int):
        unmute_time = datetime.now() + timedelta(seconds= time_sec)

        await cls.bot.restrict_chat_member(
            chat_id= chat_id,
            user_id= user_id,
            until_date= unmute_time,
            permissions= cls.permissions(can_send_messages= False)
        )


    def notice_bad_words(cls, text) -> list:
        noticed_bad_words = [
            bad_word for bad_word in cls.bad_words
            if bad_word in text
        ]

        return noticed_bad_words
    
    
    def permissions(cls, can_send_messages: bool = None) -> ChatPermissions:
        if can_send_messages is None:
            return
        
        return ChatPermissions(
            can_send_messages= can_send_messages,
            can_send_media_messages= can_send_messages,
            can_send_polls= False,
            can_send_other_messages= False,
            can_add_web_page_previews= False,
            can_change_info= True,
            can_invite_users= True,
            can_pin_messages=False,
        )
    

    async def check_bad_words(cls, message: Message):
        
        if 'group' not in message.chat.type:
            return
        
        noticed_bad_words = cls.notice_bad_words(message.text)

        if not noticed_bad_words:
            return
        
        try:
            await cls.mute(message.chat.id, message.from_user.id, 60)

        except (CantRestrictChatOwner, UserIsAnAdministratorOfTheChat):
            return
        
        await message.delete()

        username = message.from_user.username
        user_id = message.from_user.id

        text = "@{name} (ID: {id}), Ваше сообщение содержит недопустимые слова и было удалено + mute"
        text = text.format(name= username, id= user_id)

        await message.answer(text)
        
        chat_name = message.chat.username
        if isinstance(chat_name, str):
            chat_name = "".join(["\n(@", chat_name, ") "])
            
        if chat_name is None:
            chat_name = ""

        explain_text = "⚠️🙂 Следующие слова в чате {title} {name}запрещены:\n\n{bad_words}".format(
            title= message.chat.full_name,
            name= chat_name,
            bad_words= ", ".join(noticed_bad_words),
        )
        
        await cls.bot.send_message(chat_id=user_id, text= explain_text)
        