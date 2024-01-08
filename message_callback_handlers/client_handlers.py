# from typing import Any
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from create_bot import ADMIN_ID, bot
from general_logic.universal_keyboard_manager import GeneralKeyboardManager
from general_logic.client_interaction import handle_first_entry, handle_start_menu

clicked_users = {}


async def handle_user_click(
    user_id: int, button_data: str, callback_query
) -> bool:
    """
    Checks if users pushed the order_button -> return true.
    Else - put user_id and order number in clicked-users dict as key: value and return false.
    """
    if user_id in clicked_users and clicked_users[user_id] == button_data:
        await bot.answer_callback_query(
            callback_query.id,
            text=f"{button_data}\n\nВы уже откликнулись",
            show_alert=True,
        )
        return True
    clicked_users[user_id] = button_data
    return False


def register_client(dp: Dispatcher) -> None:
    """
    Registrates callback and text handlers for client interface.
    """

    @dp.callback_query_handler(
        lambda query: query.data and query.data.startswith("order_")
    )
    async def handle_client_order_callback(callback_query: types.CallbackQuery):
        """
        Extracts user ID and application number from callback query of pressed button,
        explains to client work logic of this bot,
        asks client to send conditions under which he is ready to conclude a contract.
        """
        user_id = callback_query.from_user.id
        button_data = callback_query.data.replace("order_", "")
        already_clicked_users = await handle_user_click(
            user_id, button_data, callback_query)
        if not already_clicked_users:
            await bot.answer_callback_query(
                callback_query.id,
                text=f"{button_data}\n\nУкажите стоимость и сроки, ответив на последнее присланное сообщение от бота.",
                show_alert=True, )
            await bot.send_message(
                chat_id=user_id,
                text=f"{button_data}\n\nДобрый день,\nукажите через запятую:\n      1)стоимость\n      2)сроки\nза которые Вы готовы выполнить данный контракт\n\n\n *чтобы ответить - выделите данное сообщение и нажмите 'ответить'",  )
        await bot.answer_callback_query(callback_query.id)

    @dp.message_handler(lambda message: message.reply_to_message is not None)
    async def handle_reply_from_client(message: types.Message) -> None:
        """
        Retrieves internal data in the client response message: user ID, name, and text.
        Creates and sends message to the administrator or clients, depending on the incoming data.
        """
        user_id = message.from_user.id
        replied_message = message.reply_to_message
        if replied_message and replied_message.text:
            user_reply_text = message.text
            title_parts = replied_message.text.split("\n")
            button_data = " ".join(title_parts[:1])
            message_text = f"{button_data} от id: {user_id}\n\n"
            user_name = message.from_user.username
            chat_link = (
                f"\n\nПерейти в чат: https://t.me/{user_name}"
                if user_name is not None
                else "\n\nЛичный чат не доступен, у пользователя скрыто имя"
            )
            message_text += user_reply_text
            message_text += chat_link
            keyboard = await GeneralKeyboardManager.create_inline_keyboard(
                f"Ответить от имени бота", f"answer_bot_{user_id}\n{button_data}"
            )
            await bot.send_message(
                chat_id=ADMIN_ID, text=message_text, reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text="Заявка уже не актуальна, пожалуйста, нажимте на кнопку актуальные заявки.",
            )

    dp.register_message_handler(
        handle_start_menu, Text(equals="актуальные заявки", ignore_case=True)
    )
    dp.register_message_handler(handle_first_entry)
