from .polls import MessagePoll




class Poll:

    def __init__(cls, bot, dp):
        cls.message = MessagePoll(dp, bot)
