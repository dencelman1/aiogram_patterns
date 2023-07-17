from aiogram.types import Message
from .terminal_response import TerminalResponse
from .python_terminal import PythonTerminal
from aiogram.utils.exceptions import MessageIsTooLong





class Terminal:

    MAX_MESSAGE_LENGTH = 4096

    def __init__(self):
        self.terminal_users = []
        self.py = PythonTerminal()


    async def response(self, message: Message):
        if message.from_user.id not in self.terminal_users:
            await message.answer("to connect to terminal - /con")
            return
        
        resp = await TerminalResponse.new(message.text)
        await self.send_response(message, resp)

        
    async def send_response(self, message: Message, resp:str):
        try:
            await message.answer(resp)

        except MessageIsTooLong:
            lines = [
                resp[i:i+self.MAX_MESSAGE_LENGTH]
                for i in range(0, len(resp), self.MAX_MESSAGE_LENGTH)
            ]

            for line in lines:
                await message.answer(line)

        except Exception as e:
            await message.answer(str(e))


    async def connect(self, message: Message):
        user_id = message.from_user.id
        if user_id not in self.terminal_users:
            self.terminal_users.append(user_id)
            await message.answer("connected to bot terminal")


    async def disconnect(self, message: Message):
        user_id = message.from_user.id
        if user_id in self.terminal_users:
            self.terminal_users.remove(user_id)
            await message.answer("disconnected from bot terminal")
