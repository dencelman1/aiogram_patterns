from aiogram.types import Message
from io import StringIO
import html
import sys
from aiogram.utils.exceptions import MessageTextIsEmpty



class PythonTerminal:

    def __init__(self):
        self.terminal_users = []
        self.vars = {}


    async def response(self, message: Message):
        user_id = message.from_user.id

        if user_id not in self.terminal_users:
            await message.answer("to /con")
            return
        
        output = StringIO()
        sys.stdout = output

        exec(message.text, {}, self.vars)

        resp = output.getvalue()
        resp = html.escape(resp)

        try:
            await message.answer(resp)
            
        except MessageTextIsEmpty:
            pass

        


    
    async def connect(self, message: Message):
        user_id = message.from_user.id
        if user_id not in self.terminal_users:
            self.terminal_users.append(user_id)
            await message.answer("connected to python terminal")


    async def disconnect(self, message: Message):
        user_id = message.from_user.id
        if user_id in self.terminal_users:
            self.terminal_users.remove(user_id)
            await message.answer("disconnected from python terminal")