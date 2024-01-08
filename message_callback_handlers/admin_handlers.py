from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from create_bot import ADMIN_ID, bot
from general_logic.admin_answer_from_bot import BotAnswersClass
from general_logic.admin_card_manager import AdminStateManager, AdminLogic
from sql_logic import sqlite_db


def register_admin(dp: Dispatcher):
    """
    Registrates callback and text handlers for admin interface.
    """
    @dp.callback_query_handler(
        lambda callback_query: callback_query.data.startswith("answer_bot_")
    )
    async def handle_admin_answer(
        callback_query: types.CallbackQuery, state: FSMContext
    ):
        await BotAnswersClass.user_id.set()
        async with state.proxy() as data:
            data["user_id"] = int(
                callback_query.data.split("\n")[0].replace("answer_bot_", "")
            )
            user_id = data["user_id"]
        await BotAnswersClass.order_number.set()
        async with state.proxy() as data:
            data["order_number"] = callback_query.data.split("\n")[1]
            order_number = data["order_number"]
        await BotAnswersClass.answer.set()
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Введите ответ от имени бота\nдля пользователя id: {user_id}\nпо {order_number}",
        )

    @dp.callback_query_handler(lambda x: x.data and x.data.startswith("del "))
    async def handle_calback_del(callback_query: types.CallbackQuery):
        await sqlite_db.sql_delete_command(callback_query.data.replace("del ", ""))
        await callback_query.answer(
            text=f'{callback_query.data.replace("del ","")} удалена.', show_alert=True
        )

    dp.register_message_handler(
        AdminStateManager.make_changes_commands,
        Text(equals="модератор", ignore_case=True),
    )
    dp.register_message_handler(
        AdminStateManager.cancel_handler,
        Text(equals="отмена", ignore_case=True),
        state="*",
    )

    dp.register_message_handler(
        AdminStateManager.cm_start,
        Text(equals="загрузить", ignore_case=True),
        state=None,
    )
    dp.register_message_handler(
        AdminStateManager.cancel_handler, state="*", commands="отмена"
    )
    dp.register_message_handler(
        AdminStateManager.load_document,
        content_types=["document"],
        state=AdminStateManager().document,
    )
    dp.register_message_handler(
        AdminStateManager.load_none_document,
        Text(equals="загрузить без файла", ignore_case=True),
        state=None,
    )
    dp.register_message_handler(
        AdminStateManager.load_name, state=AdminStateManager.name
    )
    dp.register_message_handler(
        BotAnswersClass.admin_answer_from_bot, state=BotAnswersClass.answer
    )
    dp.register_message_handler(
        AdminStateManager.load_discription, state=AdminStateManager.discription
    )
    dp.register_message_handler(
        AdminStateManager.load_terms, state=AdminStateManager.terms
    )
    dp.register_message_handler(
        AdminLogic.delete_item, Text(equals="удалить", ignore_case=True)
    )
