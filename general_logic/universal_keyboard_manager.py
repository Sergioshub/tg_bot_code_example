from typing import List

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


class GeneralKeyboardManager:
    @staticmethod
    def create_keyboard(*buttons: List[str]) -> ReplyKeyboardMarkup:
        """
        Creates a keyboard layout with provided buttons.
        Args:
            *buttons: Variable number of button names as strings.
        Returns:
            ReplyKeyboardMarkup: Keyboard layout object with provided buttons.
        """
        buttons_list = [KeyboardButton(button_name) for button_name in buttons]
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(*buttons_list)
        return keyboard

    @classmethod
    async def create_inline_keyboard(
        cls, button_text: str, button_data: str
    ) -> InlineKeyboardMarkup:
        """
        This method generates an inline single button.
        The button generated by this method is used for applying(client)
        or deleting(admin) an action below product cards.

        Args:
            button_text: Text for the button.
            button_data: Callback data for the button.
        Returns:
            InlineKeyboardMarkup: The created inline keyboard.
        """
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(button_text, callback_data=button_data))
        return keyboard


admin_keyboard = GeneralKeyboardManager.create_keyboard(
    "загрузить", "загрузить без файла", "удалить"
)
client_keyboard = GeneralKeyboardManager.create_keyboard("Актуальные заявки")
