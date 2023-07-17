from .small.keyboard import Keyboard




class SmallPattern:

    PATTERN_NAMES_WITH_CALLBACKS: list[str] = []

    def __init__(cls):
        cls.keyboard = Keyboard()
