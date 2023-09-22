import os
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

from create_bot import dp, bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext


from keyboards.keyboards_ru import menu_kb, in_text_davinci_003_kb, model_settings_kb, max_length_kb, temperature_replykeyboard, temperature_inlinekeyboard, language_kb, model_kb, return_kb, in_gpt_turbo_kb


from data_base.sqlite_db import Database, All_states


class Form(StatesGroup):
  in_gpt_turbo_ru = State()
  in_text_davinci_003_ru = State()
  in_model_settings_ru = State()
  in_choose_model_ru = State()
  in_max_length_ru = State()
  in_temperature_ru = State()



db = Database('user_settings.db')
 


                     ### Chat with Sparkie ###
#@dp.message_handler(Text(equals='Chat with Sparkie'))
async def chat_with_sparkie_ru(message: Message):
  user_id = message.from_user.id
  model = get_model(db, user_id)
  if model == 'gpt-3.5-turbo':
    await Form.in_gpt_turbo_ru.set()
    reply_markup = in_gpt_turbo_kb
  elif model == 'text-davinci-003':
    await Form.in_text_davinci_003_ru.set()
    reply_markup = in_text_davinci_003_kb
  await bot.send_message(user_id, "Приветствую вас в чате. Сформулируйте свой вопрос и отправьте мне. Будьте внимательны к количеству токенов, которые есть на вашем счету.", reply_markup=reply_markup)


                ### in_gpt_turbo handler ###
#@dp.message_handler(state=Form.in_gpt_turbo_ru)
async def in_gpt_turbo_ru(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '⬅️':
    await state.finish()
    await bot.send_message(user_id, "Добро пожаловать в главное меню. Пожалуйста, выберите одну из опций:", reply_markup=menu_kb)
  elif message.text == "🕹\nВыбрать модель":
    await Form.in_choose_model_ru.set()
    await bot.send_message(user_id, f"Ваша текущая модель - это {get_model(db, user_id)}.", reply_markup=return_kb)
    await bot.send_message(user_id, "Выберите одну из доступных моделей:", reply_markup=model_kb)
  else:
    try:
      completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
      {"role": "user", "content": f"{message.text}\n"}
      ]
      )
      await bot.send_message(user_id, completion["choices"][0]["message"]["content"])
      tokens = get_token_balance(db, user_id)
      num_tokens_used = completion["usage"]["total_tokens"]
      print('\nnum_tokens_used:' ,num_tokens_used)
      subtract_tokens(db, user_id, num_tokens_used)
      await bot.send_message(user_id, f"Баланс токенов: {tokens-num_tokens_used}")
    except Exception as e:
      await bot.send_message(user_id, "Во время взаимодействия с моделью произошла ошибка. Пожалуйста, попробуйте ещё раз позже.")
      print(e)
    

            ### in_text_davinci_003 handler ###
#@dp.message_handler(state=Form.in_text_davinci_003_ru)
async def in_text_davinci_003_ru(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '⬅️':
    await state.finish()
    await bot.send_message(user_id, "Добро пожаловать в главное меню. Пожалуйста, выберите одну из опций:", reply_markup=menu_kb)
  elif message.text == "⚙️\nНастройки модели":
    await Form.in_model_settings_ru.set()
    await bot.send_message(user_id, "Выберите одну из настроек:", reply_markup=model_settings_kb)
  elif message.text == "🕹\nВыбрать модель":
    await Form.in_choose_model_ru.set()
    await bot.send_message(user_id, f"Ваша текущая модель - это {get_model(db, user_id)}.", reply_markup=return_kb)
    await bot.send_message(user_id, f"Выберите одну из доступных моделей:", reply_markup=model_kb)
  else:
    try:
### check if a user's token balance is less than the max length ###
      tokens, max_length, temperature = get_text_davinci_003_settings(db, user_id)
      print(tokens, max_length, temperature)
      if tokens < max_length:
        await bot.send_message(user_id, f"Недостаточное количество токенов на счету: {tokens}")
        return
      completion = openai.Completion.create(
      engine="text-davinci-003",
      prompt=(f"{message.text}\n"),
      max_tokens=max_length,
      n = 1,
      stop=None,
      temperature=temperature,
      )
      await bot.send_message(user_id, completion["choices"][0]["text"])
      num_tokens_used = completion["usage"]["total_tokens"]
      print('num_tokens_used:' ,num_tokens_used)
      subtract_tokens(db, user_id, num_tokens_used)
      await bot.send_message(user_id, f"Баланс токенов: {tokens-num_tokens_used}")
    except Exception as e:
      await bot.send_message(user_id, "Во время взаимодействия с моделью произошла ошибка. Пожалуйста, попробуйте ещё раз позже.")
      print(e)

                ### In_prompt_settings handler ###
#@dp.message_handler(state=Form.in_model_settings_ru)
async def in_prompt_settings_ru(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '⬅️':
    await Form.in_text_davinci_003_ru.set()
    await bot.send_message(user_id, "Вы можете продолжать общение.", reply_markup=in_text_davinci_003_kb)
  elif message.text == 'Максимальная длина':
    await Form.in_max_length_ru.set()
    current_max_length = get_max_length(db, user_id)
    await bot.send_message(user_id, f"Ваша текущая Максимальная длина составляет: {current_max_length}.\nПожалуйста, введите необходимую длину:", reply_markup=max_length_kb)
  elif message.text == 'Температура':
    await Form.in_temperature_ru.set()
    current_temperature = get_temperature(db, user_id)
    await bot.send_message(user_id, f"Ваша текущая Температура составляет: {current_temperature}.", reply_markup=temperature_replykeyboard)
    await bot.send_message(user_id, "Пожалуйста, выберите необходимое вам значение:", reply_markup=temperature_inlinekeyboard)

                  ### Processing Max_length ###
#@dp.message_handler(state=Form.in_max_length_ru)
async def in_max_length_ru(message: Message, state: FSMContext):
  user_id = message.from_user.id
  try:
    max_length = int(message.text)
    if max_length > 4097:
      await bot.send_message(user_id, "Максимальная длина для этой модели составляет 4097 токенов, которые распределяются между входящим текстом и результатом.")
    elif  max_length < 1:
      await bot.send_message(user_id, "Максимальная длина не может быть меньше 1.")
    else:
      update_max_length(db, user_id, max_length)
      await Form.in_model_settings_ru.set()
      await bot.send_message(user_id, f"Максимальная длина была изменена на {max_length}.", reply_markup=model_settings_kb)
  except ValueError:
    if message.text == '⬅️':
      await Form.in_model_settings_ru.set()
      await bot.send_message(user_id, "Выберите одну из настроек:", reply_markup=model_settings_kb)
    elif message.text == "�":
      current_max_length = get_max_length(db, user_id)
      await bot.send_message(user_id, f"Максимальная длина - это максимальное количество токенов, которые могут быть сгенерированы за один раз. Один токен соответствует приблизительно 4 символам для обычного текста.\nВы можете использовать до 4097 токенов, которые распределяются между входящим текстом и результатом.\n\nВаша текущая максимальная длина составляет: {current_max_length}\nПожалуйста, выберите необходимое вам значение:", reply_markup=max_length_kb)
    else:
      await bot.send_message(user_id, "Пожалуйста, введите числовое значение.")

                ### In_temperature inline handler ###
#@dp.callback_query_handler(lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state = Form.in_temperature_ru)
async def in_temperature_inline_ru(callback_query: CallbackQuery, state: FSMContext):
  user_id = callback_query.from_user.id
  temperature = float(callback_query.data)
  if 0 <= temperature <= 1:
    update_temperature(db, user_id, temperature)
    await Form.in_model_settings_ru.set()
    await bot.send_message(user_id, f"Температура была установлена на уровне: {temperature}.", reply_markup=model_settings_kb)

    
                ### In_temperature reply handler ###
#@dp.message_handler(state=Form.in_temperature_ru)
async def in_temperature_reply_ru(message: Message, state: FSMContext):
  user_id = message.from_user.id
  try:
    temperature = float(message.text)
    if 0 <= temperature <= 1:
      update_temperature(db, user_id, temperature)
      await Form.in_model_settings_ru.set()
      await bot.send_message(user_id, f"Температура была установлена на уровне {temperature}.", reply_markup=model_settings_kb)
    else:
      raise ValueError
  except ValueError:
    if message.text == "⬅️":
      await Form.in_model_settings_ru.set()
      await bot.send_message(user_id, "Выберите одну из настроек:", reply_markup=model_settings_kb)
    elif message.text == "�":
      current_temperature = get_temperature(db, user_id)
      await bot.send_message(user_id, f"Температура контролирует креативность и случайность ответов, созданных лингвистической моделью. Низкая температура приведет к более консервативным и детерминированным ответам, тогда как более высокая температура создаст более разнообразные и непредсказуемые ответы. Температуру можно настроить в зависимости от желаемого уровня креативности и логической связности для конкретной задачи.\n\nВаша текущая Температура составляет: {current_temperature}. Пожалуйста, выберите нужное вам значение:", reply_markup=temperature_inlinekeyboard)
    else:
      await bot.send_message(user_id, "Температура должна быть числовым значением от 0 до 1.", reply_markup=temperature_inlinekeyboard)
    


              ### In choose model inline keyboard ###
#@dp.callback_query_handler(lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state = Form.in_choose_model_ru)
async def in_choose_model_inline_ru(callback_query: CallbackQuery, state: FSMContext):
  user_id = callback_query.from_user.id
  model = callback_query.data
  if model == "gpt-3.5-turbo":
    change_model(db, user_id, model)
    await Form.in_gpt_turbo_ru.set()
    reply_markup = in_gpt_turbo_kb
  elif model == 'text-davinci-003':
    change_model(db, user_id, model)
    await Form.in_text_davinci_003_ru.set()
    reply_markup = in_text_davinci_003_kb
  await bot.send_message(user_id, f"Модель была изменена на {model}. Вы можете продолжать общение.", reply_markup=reply_markup)


            ### In choose model reply keyboard ###
#@dp.message_handler(state=Form.in_choose_model_ru)
async def in_choose_model_reply_ru(message: Message, state: FSMContext):
  user_id = message.from_user.id
  current_model = get_model(db, user_id)
  if message.text == '⬅️':
    if current_model == "gpt-3.5-turbo":
      chat_keyboard = in_gpt_turbo_kb
      await Form.in_gpt_turbo_ru.set()
    elif current_model == "text-davinci-003":
      chat_keyboard = in_text_davinci_003_kb
      await Form.in_text_davinci_003_ru.set()
    await bot.send_message(user_id, "Приветствую вас в чате. Сформулируйте свой вопрос и отправьте мне. Будьте внимательны к количеству токенов, которые есть на вашем счету.", reply_markup=chat_keyboard)
  elif message.text == '�':
    await bot.send_message(user_id, "Модели GPT-3.5 могут понимать и генерировать натуральную речь или код.\n\n🤖  gpt-3.5-turbo - Самая мощная модель GPT-3.5, которая оптимизирована для чатов и работает за 1/10 от стоимости text-davinci-003.\n\n🤖  text-davinci-003 - Может выполнять любую лингвистическую задачу и дает возможность контролировать Максимальную длину и Температуру.", reply_markup=return_kb)
    
  
  
    
    


        
    


  

#@dp.message_handler(commands=['/Create_content'])
async def command_create_content_ru(message: Message):
  await bot.send_message(message.from_user.id, 'Choose one of the provided publishing styles or click the button "Your content"', reply_markup=choose_content_type_kb)

#@dp.message_handler(commands=['/Generate_a_picture'])
async def generate_a_picture_ru(message: Message):
  await bot.send_message(message.from_user.id, 'Опишите, что вы хотите сгенерировать, или воспользуйтесь нашим руководством эффективного промптинга, чтобы получить максимальный результат.')


  

                     ### Registering Handlers ###
def register_handlers_client_RU(dp : Dispatcher):
  dp.register_message_handler(chat_with_sparkie_ru, Text(equals='💬 Чат со Sparky'))
  dp.register_message_handler(in_gpt_turbo_ru, state=Form.in_gpt_turbo_ru)
  dp.register_message_handler(in_text_davinci_003_ru, state=Form.in_text_davinci_003_ru)
  dp.register_message_handler(in_prompt_settings_ru, state=Form.in_model_settings_ru)
  dp.register_message_handler(in_max_length_ru, state=Form.in_max_length_ru)
  dp.register_callback_query_handler(in_temperature_inline_ru, lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state=Form.in_temperature_ru)
  dp.register_message_handler(in_temperature_reply_ru, state=Form.in_temperature_ru)
  dp.register_callback_query_handler(in_choose_model_inline_ru, lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state=Form.in_choose_model_ru)
  dp.register_message_handler(in_choose_model_reply_ru, state=Form.in_choose_model_ru)
  dp.register_message_handler(generate_a_picture_ru, Text(equals='🖼️ Сгенерировать изображение'))
  #dp.register_message_handler(command_create_content_ru, Text(equals='Create content'))
  


      ### callback query handler to handle the callback data sent by the inline buttons when "Create content" is pressed ###
  
@dp.callback_query_handler(lambda c: c.data in ["post", "article", "story", "business letter", "commercial", "your content"])
async def process_create_content_ru(callback_query: CallbackQuery):
    data = callback_query.data
    if data == "post":
        # Do something for button 1
        await callback_query.answer("Button Post pressed")
    elif data == "article":
        # Do something for button 2
        await callback_query.answer("Button Article pressed")
    elif data == "story":
        # Do something for button 2
        await callback_query.answer("Button Story pressed")
    elif data == "business letter":
        # Do something for button 2
        await callback_query.answer("Button Business letter pressed")
    elif data == "commercial":
        # Do something for button 2
        await callback_query.answer("Button Commercial pressed")
    elif data == "your content":
        # Do something for button 2
        await callback_query.answer("Button Your content pressed")


