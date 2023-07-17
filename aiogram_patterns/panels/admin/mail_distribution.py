from aiogram import Bot




class MailDistribution:

    def __init__(cls, bot: Bot):
        cls.bot = bot
        
    
    async def send_message(cls, receivers: list[int], text: str, *args, **kwargs) -> int:
        """:return: int number of successfully sent messages to receivers"""

        if not receivers or not isinstance(receivers, list):
            receivers = []

        args, kwargs = list(args), dict(kwargs)

        send_out = 0
        for receiver_id in receivers:
            try:
                await cls.bot.send_message(chat_id= receiver_id, text= text, *args, **kwargs)
                send_out += 1

            except Exception as exc:
                error_message = f"Not sended message to user with id = {receiver_id}"
                cls.print_error(cls.send_message, error_message)

        return send_out
    

    def print_error(cls, func, message):
        print(f"[{cls.__class__} => {func.__name__}()]: {message}")
        