from aiogram_patterns import AiogramPatterns
from aiogram.types import Message
import asyncio

token = 1



class SimpleAskBot(AiogramPatterns):

    def __init__(self):
        super().__init__(token)
        self.dp.register_message_handler(self.ask, commands=['start'])


    async def ask(self, message: Message):
        message_poll = self.pattern.medium.poll.message

        questions = ['ваше имя', 'сколько лет']

        await message_poll.ask(
            chat_id= message.chat.id,
            questions=questions,
            callback=self.callback_ask,
        )


    async def callback_ask(self, message: Message, result:dict):
        result = ["{}: {}".format(question, answer) for question, answer in result.items()]
        result = "\n".join(result)

        await message.answer(result)





async def main():
    my_bot = SimpleAskBot()
    await my_bot.run()
    


if __name__ == "__main__":
    asyncio.run(main())
    


