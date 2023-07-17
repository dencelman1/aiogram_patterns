from .dba import DBA
from .mail_distribution import MailDistribution




class AdminPanel:

    def __init__(cls, bot):
        cls.dba = DBA()
        cls.mail_distribution = MailDistribution(bot)

        cls.bot = bot