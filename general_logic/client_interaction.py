from aiogram import types
from create_bot import bot
from general_logic.universal_card_sender import send_data
from general_logic.universal_keyboard_manager import client_keyboard, GeneralKeyboardManager
from sql_logic import sqlite_db

MESSAGE_GREET = (
    "Добрый день!\n"
    "Это чат, в котором мы публикуем все работы по экспертизе промышленной безопасности.\n"
    'Чтобы взять заявку - нажмите на "Актуальные заявки".'
)


async def handle_first_entry(message: types.Message, bot_instance=bot) -> None:
    """
    Sends the greeting message and stores the user ID in the database.
    """
    user_id = message.from_user.id
    await bot_instance.send_message(
        message.from_user.id,
        MESSAGE_GREET,
        reply_markup=client_keyboard,
    )
    await message.delete()
    await sqlite_db.sql_add_user_to_list(user_id)


async def handle_start_menu(message: types.Message, bot_instance=bot) -> None:
    """
    Handles the start menu for the user.
    """
    user_id = message.from_user.id
    read = await sqlite_db.check_items(user_id)
    if read:
        for ret in read:
            keyboard = await GeneralKeyboardManager.create_inline_keyboard(
                f"Откликнуться на {ret[1]}", f"order_{ret[1]}"
            )
            await send_data(bot_instance, user_id, ret, keyboard)
