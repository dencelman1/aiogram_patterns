from .medium import Feedback, Pagination, Poll, \
    Terminal, Api, Localization

from aiogram import Bot, Dispatcher




class MediumPattern:

    PATTERN_NAMES_WITH_CALLBACKS: list[str] = [
        'feedback',
        'pagination',
    ]

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.pagination = Pagination()
        self.feedback = Feedback(bot, dp)
        self.poll = Poll(bot, dp)
        self.terminal = Terminal()
        self.api = Api
        self.localization = Localization()
        