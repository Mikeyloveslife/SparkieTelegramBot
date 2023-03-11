import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

telegramBot_api = os.environ['telegramBot_api']

bot = Bot(token=telegramBot_api)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)