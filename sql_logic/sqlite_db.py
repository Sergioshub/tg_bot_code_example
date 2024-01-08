from typing import Any, Union

import sqlite3 as sql

from aiogram import exceptions
from create_bot import ADMIN_ID, bot
from general_logic.universal_card_sender import send_data
from general_logic.universal_keyboard_manager import GeneralKeyboardManager
from sql_logic import sqlite_db


async def users_counter() -> int:
    """
    Function counts all saved users in db and returns count of them, if they exsist.
    """
    users_list = await sql_read_user_list()
    if users_list:
        return len(users_list)
    return 0


base = None
cur = None


async def sql_start() -> None:
    """
    Function connects to the database, creates tables if they don't exist,
    and sets global variables 'base' and 'cur' for further usage in other functions.
    """
    global base, cur
    try:
        with sql.connect("exp.db") as base:
            cur = base.cursor()
            if base:
                print("Data base connected ok!")
                users_count = await users_counter()
                print(f"Колличество id, сохраненных в базе данных: {users_count}")
            base.execute(
                "CREATE TABLE IF NOT EXISTS menu(img TEXT, name TEXT PRIMARY KEY, desription TEXT, price TEXT)"
            )
            base.execute(
                "CREATE TABLE IF NOT EXISTS user_list(user_id TEXT PRIMARY KEY)"
            )
            base.commit()
    except sql.Error as e:
        print(
            f"Error occurred while connecting to the database or creating tables: {e}"
        )


async def sql_add_product_card(state) -> None:
    """
    Funstion inserts tuple of product's card data to DB.
    """
    async with state.proxy() as data:
        try:
            cur.execute("INSERT INTO menu VALUES(?,?,?,?)", tuple(data.values()))
            base.commit()
            await sqlite_db.sendall()
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"Рассылка заявки произведена, кол-во контактов в базе: {await users_counter()}",
            )
        except sql.IntegrityError:
            await bot.send_message(
                chat_id=ADMIN_ID,
                text="Возникла ошибка. Пожалуйста, повторите ввод. Вероятно, файл с таким названием уже существует",
            )
            return


async def fetch_all_items() -> list[Any]:
    """
    Function retrieves and returns a list of product cards sorted by their names from the database
    """
    try:
        return cur.execute(
            'SELECT * FROM menu ORDER BY CAST(SUBSTR(name, INSTR(name, " ")+1) AS INTEGER)'
        ).fetchall()
    except sql.Error as e:
        print(f"An error occurred while sorting product cards in the database: {e}")
        message_error = "Заявки в данный момент выводятся не по порядку, так как в одном из имен файлов нет номера заявки, или отсутствует пробел, или лишний."
        bot.send_message(chat_id=ADMIN_ID, text=message_error)
        return cur.execute("SELECT * FROM menu").fetchall()


async def fetch_last_item() -> list[Any]:
    """
    Function retrieves and returns a last added product card from the database.
    """
    return (cur.execute("SELECT * FROM menu ORDER BY ROWID DESC LIMIT 1").fetchall())[0]


async def check_items(
    user_id: int = None,
    admin_id: bool = False,
    dell: bool = False,
    last: bool = False
) -> Union[list, None]:
    """
    Checks for available products in the database and returns them.
    If it's False, the bot sends messages to the client or admin accordingly.
    """
    if last:
        read = await fetch_last_item()
    else:
        read = await fetch_all_items()

    if read:
        return read

    message_no_data_to_deletion = "Нет доступных данных для удаления.\nБаза пуста."
    message_no_request = "К сожалению у нас пока нету заявок"

    if admin_id and dell:
        await bot.send_message(ADMIN_ID, message_no_data_to_deletion)
    else:
        await bot.send_message(user_id, message_no_request)

    return None


async def sql_add_user_to_list(user_id: int) -> None:
    """
    Checks if user is not exist in DB -> put him there.
    """
    try:
        existing_user_ids = await sql_read_user_list()
        existing_user_ids = [int(user_id[0]) for user_id in existing_user_ids]

        if user_id not in existing_user_ids:
            cur.execute("INSERT INTO user_list VALUES (?)", (user_id,))
            base.commit()
    except sql.Error as e:
        print(f"Ошибка при добавлении пользователя в базу: {e}")


async def sql_read_user_list() -> list[Any] | None:
    """
    Returns all availible users from table 'users_list' in DB.
    """
    try:
        return cur.execute("SELECT user_id FROM user_list").fetchall()
    except sql.Error as e:
        print(f"An error occurred while extracting users from DB: {e}")


async def check_users() -> list[Any] | None:
    """
    Checks and returns if users exist in the database.
    Otherwise sands message to admin about it.
    """
    message_no_user_in_db = "В базе нету id пользователей для рассылки"
    user_list = await sql_read_user_list()
    if not user_list:
        bot.send_message(chat_id=ADMIN_ID, text=message_no_user_in_db)
    return user_list


async def sql_delete_command(data) -> None:
    """
    Deletes from the 'menu' table the product card by its name.
    """
    try:
        cur.execute("DELETE FROM menu WHERE name == ?", (data,))
        base.commit()
    except sql.Error as e:
        print(f"An error occurred while deleting product card: {e}")


async def sql_delete_user(user_id) -> None:
    """Function try to delete user(s), who have blocked this bot."""
    try:
        cur.execute(
            "DELETE FROM user_list WHERE user_id = ?",
            (user_id),
        )
        base.commit()
    except sql.Error as e:
        print(
            f"An error occurred while deleting user(s) who have blocked this bot: {e}"
        )


async def sendall() -> None:
    """
    Function sands the last added to DB product card to all users from DB.
    """
    user_list = await sqlite_db.check_users()
    if user_list:
        for user_id in user_list:
            last_item = await sqlite_db.check_items(admin_id=True, last=True)
            if last_item:
                try:
                    keyboard = (
                        await GeneralKeyboardManager.create_inline_keyboard(
                            f"Отликнуться на {last_item[1]}", f"order_{last_item[1]}"
                        )
                        if user_id != ADMIN_ID
                        else None
                    )
                    await send_data(bot, user_id[0], last_item, keyboard)
                except exceptions.BotBlocked:
                    await sqlite_db.sql_delete_user(user_id)
