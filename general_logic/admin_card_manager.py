from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from create_bot import bot, ADMIN_ID, STUFF_ID
from general_logic.universal_keyboard_manager import (
    admin_keyboard,
    GeneralKeyboardManager,
)
from general_logic.universal_card_sender import send_data
from sql_logic import sqlite_db


class AdminStateManager(StatesGroup):
    """
    Machine state. Beginning of product-saving block.
    """

    document = State()
    name = State()
    discription = State()
    terms = State()

    @staticmethod
    async def save_data_to_state(state: FSMContext, **kwargs):
        """
        Saves the provided data into the FSMContext state.
        """
        async with state.proxy() as data:
            for key, value in kwargs.items():
                data[key] = value

    @staticmethod
    async def make_changes_commands(message: types.Message) -> None:
        """Function to initiate admin actions."""
        if message.from_user.id in STUFF_ID:
            await bot.send_message(
                message.from_user.id,
                "Что Вы хотите сделать?",
                reply_markup=admin_keyboard,
            )
            await message.delete()

    @staticmethod
    async def cm_start(message: types.Message) -> None:
        """Function to start the process of uploading a document."""
        if message.from_user.id in STUFF_ID:
            await AdminStateManager.document.set()
            await message.reply("Загрузите документ")

    @staticmethod
    async def cancel_handler(message: types.Message, state: FSMContext) -> None:
        """Function to cancel ongoing processes."""
        if message.from_user.id in STUFF_ID:
            # current_state = await state.get_state()
            # if current_state is None:
            #     return
            await state.finish()
            await message.reply("OK")

    @staticmethod
    async def load_document(message: types.Message, state: FSMContext) -> None:
        """Loads a document or without it and prompts for a name."""
        if message.from_user.id in STUFF_ID:
            await AdminStateManager.save_data_to_state(
                state, document=message.document.file_id
            )
            await AdminStateManager.next()
            await message.reply("Теперь введите название")

    @staticmethod
    async def load_none_document(message: types.Message, state: FSMContext) -> None:
        """Loads without document and prompts for a name."""
        if message.from_user.id in STUFF_ID:
            await AdminStateManager.document.set()
            await AdminStateManager.save_data_to_state(state, document=None)
            # async with state.proxy() as data:
            #     data["document"] = None
            await AdminStateManager.next()
            await message.reply("Теперь введите название")

    @staticmethod
    async def load_name(message: types.Message, state: FSMContext) -> None:
        """Saves the name and prompts for a description."""
        if message.from_user.id in STUFF_ID:
            await AdminStateManager.save_data_to_state(state, name=message.text)
            await AdminStateManager.next()
            await message.reply("Введите описание")

    @staticmethod
    async def load_discription(message: types.Message, state: FSMContext) -> None:
        """Saves the description and prompts for terms."""
        if message.from_user.id in STUFF_ID:
            await AdminStateManager.save_data_to_state(state, description=message.text)
            await AdminStateManager.next()
            await message.reply("Введите сроки исполнения")

    @staticmethod
    async def load_terms(message: types.Message, state: FSMContext) -> None:
        """Saves the terms, adds the product card to the database, and finishes the state."""
        if message.from_user.id in STUFF_ID:
            await AdminStateManager.save_data_to_state(state, price=message.text)
            await bot.send_message(chat_id=ADMIN_ID, text="Заявка добавлена в базу")
            await sqlite_db.sql_add_product_card(state)
            await state.finish()


class AdminLogic:
    """
    Provides methods for administrative actions such as deleting service cards from the database.
    """

    @staticmethod
    async def delete_item(message: types.Message) -> None:
        """
        Sends all service cards from the database to the admin with a delete button.
        """
        user_id = message.from_user.id
        if user_id in STUFF_ID:  # Assuming GROUP_USER_ID is defined somewhere
            read = await sqlite_db.check_items(admin_id=True, dell=True)
            user_id = message.from_user.id
            if read:
                for ret in read:
                    keyboard = await GeneralKeyboardManager.create_inline_keyboard(
                        f"Удалить {ret[1]}", f"del {ret[1]}"
                    )
                    await send_data(bot, user_id, ret, keyboard)
