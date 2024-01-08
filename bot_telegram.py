from aiogram.utils import executor
from sql_logic import sqlite_db

from create_bot import dp
from message_callback_handlers.admin_handlers import register_admin
from message_callback_handlers.client_handlers import register_client


async def on_startup(_):
    """
    Starts bot instance.
    """
    print("Бот запущен")
    await sqlite_db.sql_start()


register_admin(dp)
register_client(dp)


executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
