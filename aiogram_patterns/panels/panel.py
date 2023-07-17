from .admin import AdminPanel
from .user import UserPanel

from aiogram import Bot



class Panel:

    def __init__(cls, bot: Bot):
        cls.admin = AdminPanel(bot)
        cls.user = UserPanel()
