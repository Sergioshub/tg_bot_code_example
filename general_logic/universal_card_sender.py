from aiogram.types import InlineKeyboardMarkup


async def send_data(
    bot, user_id: int, data: tuple, keyboard: InlineKeyboardMarkup
) -> None:
    """
    Sends product details, sending a document if index[0] contains one,
    otherwise sending without it.

    Args:
        bot: The bot instance.
        user_id: ID of the user to whom the data will be sent.
        data: Tuple containing information to send.
        keyboard: Optional keyboard to send with the data.
    """
    document_id = data[0]
    name = data[1]
    description = data[2]
    terms = data[-1]

    if document_id:
        await bot.send_document(
            user_id,
            document_id,
            caption=f"{name}\n\n{description}\n\nСрок: {terms}",
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(
            user_id,
            f"{name}\n\n{description}\n\nСрок: {terms}",
            reply_markup=keyboard,
        )
