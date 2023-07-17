from aiogram import Bot, Dispatcher
from .big import GroupAdmin, UsersTalk




class BigPattern:

    PATTERN_NAMES_WITH_CALLBACKS: list[str] = []

    def __init__(cls, bot: Bot, dp: Dispatcher):
        cls.group_admin = GroupAdmin(bot, dp)
        cls.users_talk = UsersTalk(bot, dp)
        