from .patterns import SmallPattern, MediumPattern, BigPattern

from aiogram import Bot, Dispatcher




class Pattern:

    PATTERN_NAMES_WITH_CALLBACKS: dict = {
        "big": BigPattern.PATTERN_NAMES_WITH_CALLBACKS,
        "medium": MediumPattern.PATTERN_NAMES_WITH_CALLBACKS,
        "small": SmallPattern.PATTERN_NAMES_WITH_CALLBACKS,
    }

    def __init__(cls, bot: Bot, dp: Dispatcher):
        cls.big = BigPattern(bot, dp)
        cls.medium = MediumPattern(bot, dp)
        cls.small = SmallPattern()
        