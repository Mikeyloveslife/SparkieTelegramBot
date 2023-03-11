from aiogram.utils import executor
from create_bot import dp, bot
from data_base import sqlite_db

async def on_startup(_):
  print('Sparkie is online')
  sqlite_db.create_database()

#from handlers.client_eng import *
from handlers.client_eng import register_handlers_client_ENG
from handlers.client_ukr import register_handlers_client_UKR
from handlers.client_ru import register_handlers_client_RU

from payments import payments_eng, payments_ukr, payments_ru

register_handlers_client_ENG(dp)
register_handlers_client_UKR(dp)
register_handlers_client_RU(dp)

from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from keyboards import keyboards_eng, keyboards_ukr, keyboards_ru
from data_base.sqlite_db import check_user_exists, get_user_lang, update_user_lang, default_user_settings


@dp.message_handler(Text(equals='/start'))
async def process_start(message: Message):
  # Get the user's Telegram ID
  user_id = message.from_user.id
  # Check if the user's Telegram ID is already in the database
  if check_user_exists(user_id):
    # Get user's language
    user_lang = get_user_lang(user_id)
    # Get the user's name 
    user = message.from_user
    name = user.first_name if user.first_name else user.username
    if user_lang == 'ENG':
      await bot.send_message(message.chat.id, f"Hi, {name}! It's great to have you back in Sparkie family!\nEvery masterpiece starts with a single idea - so start creating!", reply_markup=keyboards_eng.menu_kb)
    elif user_lang == 'UKR':
      await bot.send_message(message.chat.id, f"Вітаю, {name}! Нам дуже приємно, що ви повернулися до родини Sparkie! Кожен шедевр починається з однієї ідеї - тож починайте творити!", reply_markup=keyboards_ukr.menu_kb)
    elif user_lang == 'RU':
      await bot.send_message(message.chat.id, f"Приветствую, {name}! Рады снова видеть вас в семье Sparkie!\nКаждый шедевр начинается с единственной идеи - так что начинайте творить!", reply_markup=keyboards_eng.menu_kb)
  else:
    # New user chooses language
    await bot.send_message(message.chat.id, "Please choose your preferred lanhuage:", reply_markup=keyboards_eng.language_kb)




    
                ### Process choose language ###
@dp.callback_query_handler(lambda c: c.data in ["ENG", "UKR", "RU"])
async def choose_lang_inline(callback_query: CallbackQuery):
  # Add the user's Telegram ID to the database and set the token balance to 5000, token limit to 100 and temperature to 0.5
  user_id = callback_query.from_user.id
  data = callback_query.data
  user_lang = get_user_lang(user_id)
  tokens = 5000
  token_limit = 100
  temperature = 0.5
  model = 'gpt-3.5-turbo'
  if data == 'ENG':
    await bot.send_message(callback_query.from_user.id, "English has been installed.", reply_markup=keyboards_eng.menu_kb)
    if user_lang == None:
      default_user_settings(user_id, tokens, token_limit, temperature, model)
      await bot.send_message(callback_query.from_user.id, "Welcome to Sparkie family! We're excited to have you join our community. As a new user, you have been credited with 5000 tokens to try out our product. We hope you enjoy using our service. Let us know if you have any questions or feedback. Push one of the menu buttons to get started.", reply_markup=keyboards_eng.menu_kb)
    update_user_lang(user_id, data)
  elif data == 'UKR':
    await bot.send_message(callback_query.from_user.id, "Встановлено українську мову.", reply_markup=keyboards_ukr.menu_kb)
    if user_lang == None:
      default_user_settings(user_id, tokens, token_limit, temperature, model)
      await bot.send_message(callback_query.from_user.id, "Ласкаво просимо до родини Sparkie! Ми раді вітати вас в нашій спільноті. Як новому користувачу, вам було нараховано 5000 токенів, щоб випробувати наш продукт. Ми сподіваємося, що вам сподобається використовувати наш сервіс. Дайте нам знати, якщо у вас є якісь питання або відгуки. Натисніть одну з кнопок меню, щоб почати.", reply_markup=keyboards_ukr.menu_kb)
    update_user_lang(user_id, data)
  elif data == 'RU':
    await bot.send_message(callback_query.from_user.id, "Русский язык установлен.", reply_markup=keyboards_ru.menu_kb)
    if user_lang == None:
      default_user_settings(user_id, tokens, token_limit, temperature, model)
      await bot.send_message(callback_query.from_user.id, "Добро пожаловать в семью Sparkie! Мы рады, что вы присоединились к нашему сообществу. В качестве нового пользователя вам было начислено 5000 токенов для тестирования нашего продукта. Мы надеемся, что вам понравится использовать наш сервис. Если у вас есть вопросы или отзывы, пожалуйста, сообщите нам. Нажмите одну из кнопок меню, чтобы начать.", reply_markup=keyboards_ru.menu_kb)
    update_user_lang(user_id, data)

@dp.message_handler(Text(equals='🌐'))
async def choose_lang_reply(message: Message):
  user_id = message.chat.id
  user_lang = get_user_lang(user_id)
  if user_lang == "ENG":
    await bot.send_message(message.chat.id, "Please choose your preferred lanhuage:", reply_markup=keyboards_eng.language_kb)
  elif user_lang == "UKR":
    await bot.send_message(message.chat.id, "Будь ласка, оберіть вашу мову:", reply_markup=keyboards_ukr.language_kb)
  elif user_lang == "RU":
    await bot.send_message(message.chat.id, "Пожалуйста, выберите ваш язык:", reply_markup=keyboards_ru.language_kb)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)