from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



class InlineKeyboard:

    def __init__(cls):
        pass
    

    @staticmethod
    async def create(buttons: list) -> InlineKeyboardMarkup:

        inline_kb = InlineKeyboardMarkup()
        cls = InlineKeyboard

        for button_list in buttons:
            
            if not button_list:
                continue

            first_elem = button_list[0]
            
            if isinstance(first_elem, list):
                row_buttons = button_list

                cls.set_row_buttons(row_buttons, inline_kb)

            elif isinstance(first_elem, str):
                
                if len(button_list) == 1:
                    button_list.append("no_cb_data")

                button_data = button_list[1]

                if 'http' in button_data:
                    cls.set_link_button(button_list, inline_kb)
                    continue
                
                cls.set_single_button(button_list, inline_kb)
        
        return inline_kb


    @staticmethod
    def set_single_button(buttons: list, inline_kb: InlineKeyboardMarkup) -> None:
        name, cb_data = buttons

        button = InlineKeyboardButton(name, callback_data=cb_data)
        inline_kb.add(button)

    
    @staticmethod
    def set_link_button(buttons: list, inline_kb: InlineKeyboardMarkup) -> None:
        title, link = buttons

        button = InlineKeyboardButton(text=title, url=link)
        inline_kb.add(button)


    @staticmethod
    def set_row_buttons(
            row_buttons: list,
            inline_kb: InlineKeyboardMarkup
        ) -> None:
            
        buttons_in_row = []
        for row_button in row_buttons:
            
            if not row_button:
                continue
            
            if len(row_button) == 1:
                row_button.append("no_cb_data")

            text, cb_data = row_button
            button = InlineKeyboardButton(text, callback_data= cb_data)

            buttons_in_row.append(button)

        
        if buttons_in_row:
            inline_kb.row(*buttons_in_row)