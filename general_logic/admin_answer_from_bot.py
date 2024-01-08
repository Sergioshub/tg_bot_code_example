from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from create_bot import bot, ADMIN_ID


class BotAnswersClass(StatesGroup):
    """Machine state. Bot responses on behalf of the bot."""

    user_id = State()
    order_number = State()
    answer = State()

    @staticmethod
    async def admin_answer_from_bot(message: types.Message, state: FSMContext) -> None:
        """Function for admin to send an answer from the bot."""
        if message.from_user.id == ADMIN_ID:
            async with state.proxy() as data:
                data["answer"] = message.text
        message_text = data["order_number"]
        message_text += "\n\n"
        message_text += data["answer"]
        message_text += "\n\n\n *Чтобы ответить - выделите данное сообщение и нажмите кнопку 'ответить'"
        await bot.send_message(chat_id=data["user_id"], text=message_text)
        await state.finish()
