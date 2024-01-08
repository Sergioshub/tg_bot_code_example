from aiogram import Bot #бот и анотации
from aiogram.dispatcher import Dispatcher #реакция на события
from aiogram.contrib.fsm_storage.memory import MemoryStorage #позволяет хранить данные в оперативной памяти

storage=MemoryStorage()

bot=Bot(token='')

dp=Dispatcher(bot, storage=storage)

ADMIN_ID = 1444643206
STUFF_ID = [1444643206, 1864340449]
DEVELOPER_ID = 1444643206