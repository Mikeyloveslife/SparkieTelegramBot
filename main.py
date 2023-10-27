from dotenv import load_dotenv
load_dotenv()

from aiogram.utils import executor
from create_bot import dp, bot
from data_base import sqlite_db

from handlers.client_eng import register_handlers_client_ENG
from handlers.client_ukr import register_handlers_client_UKR
from handlers.client_ru import register_handlers_client_RU

from payments import payments_eng#, payments_ukr, payments_ru
from image_generation import image_generation_eng

from aiogram.types import Message, CallbackQuery
from keyboards import keyboards_eng, keyboards_ukr, keyboards_ru
from data_base.sqlite_db import Database

db = Database('user_settings.db')

async def on_startup(_):
  Database.create_database()
  print('Sparky is online')





#@dp.message_handler(text="/start")
async def process_start(message: Message):
  # Get the user's Telegram ID
  user_id = message.from_user.id
  # Check if the user's Telegram ID is already in the database
  user_lang = db.get_param(user_id, ("language",))
  if user_lang is not None:
    # Get user's language
    print(user_id)
    print(user_lang)
    # Get the user's name 
    user = message.from_user
    name = user.first_name if user.first_name else user.username
    # Define the language-specific messages and keyboards
    language_messages = {
      'ENG': (f"Hi, {name}! It's great to have you back in Sparky family! Every masterpiece starts with a single idea - so start creating!"),
      'UKR': (f"Вітаю, {name}! Нам дуже приємно, що ви повернулися до родини Sparky! Кожен шедевр починається з однієї ідеї - тож починайте творити!"),
      'RU': (f"Приветствую, {name}! Рады снова видеть вас в семье Sparky! Каждый шедевр начинается с единственной идеи - так что начинайте творить!")
}

    keyboards = {
      'ENG': keyboards_eng.menu_kb,
      'UKR': keyboards_ukr.menu_kb,
      'RU': keyboards_eng.menu_kb
    }

    if user_lang in language_messages:
        message_text = language_messages[user_lang]
        reply_markup = keyboards[user_lang]

        await bot.send_message(user_id, message_text, reply_markup=reply_markup)
  else:
    # NEW USER CHOOSES LANGUAGE
    await in_choose_lang_reply_eng(message)


### A SELECTION OF COMMANDS TO WORK REGARDLES STATES ###
from handlers.client_eng import chat_with_sparkie_eng, check_balance, in_choose_lang_reply_eng, image_generation_eng
from aiogram.dispatcher import FSMContext

@dp.message_handler(lambda message: message.text.startswith('/'), state='*')
async def menu_handler(message: Message, state: FSMContext):
   await state.finish()
   if message.text == "/start":
     await process_start(message)
   elif message.text == "/menu":
     user_id = message.from_user.id
     user_lang = db.get_param(user_id, ("language",))
     print("in_menu_handler", user_lang)
     language_messages = {
         'ENG': ("Welcome to the main menu. Please select an option:", keyboards_eng.menu_kb),
         'UKR': ("Ласкаво просимо до головного меню. Будь ласка, оберіть одну з опцій:", keyboards_ukr.menu_kb),
         'RU': ("Добро пожаловать в главное меню. Пожалуйста, выберите одну из опций:", keyboards_ru.menu_kb)
     }
     if user_lang in language_messages:
       message_text, reply_markup = language_messages[user_lang]
     
     await message.answer(message_text, reply_markup=reply_markup)
   elif message.text == "/chat_with_sparky":
     await chat_with_sparkie_eng(message)
   elif message.text == "/image_generation":
     await image_generation_eng(message)
   elif message.text == "/check_balance":
     await check_balance(message)
   elif message.text == "/language":
     await in_choose_lang_reply_eng(message)

register_handlers_client_ENG(dp)
register_handlers_client_RU(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)