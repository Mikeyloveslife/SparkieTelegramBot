import os
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

from create_bot import dp, bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext


from keyboards.keyboards_ukr import menu_kb, in_text_davinci_003_kb, model_settings_kb, max_length_kb, temperature_replykeyboard, temperature_inlinekeyboard, language_kb, model_kb, return_kb, in_gpt_turbo_kb


from data_base.get_sqlite import *

class Form(StatesGroup):
  in_gpt_turbo_ukr = State()
  in_text_davinci_003_ukr = State()
  in_model_settings_ukr = State()
  in_choose_model_ukr = State()
  in_max_length_ukr = State()
  in_temperature_ukr = State()
    
 


                     ### Chat with Sparkie ###
#@dp.message_handler(Text(equals='Chat with Sparkie'))
async def chat_with_sparkie_ukr(message: Message):
  if get_model(message.from_user.id) == 'gpt-3.5-turbo':
    await Form.in_gpt_turbo_ukr.set()
    await bot.send_message(message.from_user.id, "Вітаю у чаті. Сформулюйте своє питання і відправте мені. Будьте уважні до кількості токенів, які є на вашому рахунку.", reply_markup=in_gpt_turbo_kb)
  if get_model(message.from_user.id) == 'text-davinci-003':
    await Form.in_text_davinci_003_ukr.set()
    await bot.send_message(message.from_user.id, "Вітаю у чаті. Сформулюйте своє питання і відправте мені. Будьте уважні до кількості токенів, які є на вашому рахунку.", reply_markup=in_text_davinci_003_kb)


                   ### Chat with Sparkie in_gpt_turbo ###
#@dp.message_handler(state=Form.in_gpt_turbo_ukr)
async def in_gpt_turbo_ukr(message: Message, state: FSMContext):
  if message.text == '\u2B05':
    await state.finish()
    await bot.send_message(message.from_user.id, "Ласкаво просимо до головного меню. Будь ласка, оберіть одну з опцій:", reply_markup=menu_kb)
  elif message.text == "🕹\nОбрати модель":
    await Form.in_choose_model_ukr.set()
    await bot.send_message(message.from_user.id, f"Ваша поточна модель - це {get_model(message.from_user.id)}.", reply_markup=return_kb)
    await bot.send_message(message.from_user.id, "Оберіть одну з доступних моделей:", reply_markup=model_kb)
  else:
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
      {"role": "user", "content": f"{message.text}\n"}
      ]
    )
    generated_text = completion["choices"][0]["message"]["content"]
    print(generated_text)
    await bot.send_message(message.from_user.id, generated_text)
    user_id = message.from_user.id
    tokens = get_token_balance(user_id)
    num_tokens_used = completion["usage"]["total_tokens"]
    print('\nnum_tokens_used:' ,num_tokens_used)
    subtract_tokens(user_id, num_tokens_used)
    await bot.send_message(message.from_user.id, f"Баланс токенів: {tokens-num_tokens_used}")
    

               ### Chat with Sparkie in_text_davinci_003 ###
#@dp.message_handler(state=Form.in_text_davinci_003_ukr)
async def in_text_davinci_003_ukr(message: Message, state: FSMContext):
  if message.text == '\u2B05':
    await state.finish()
    await bot.send_message(message.from_user.id, "Ласкаво просимо до головного меню. Будь ласка, оберіть одну з опцій:", reply_markup=menu_kb)
  elif message.text == "⚙️\nНалаштування моделі":
    await Form.in_model_settings_ukr.set()
    await bot.send_message(message.from_user.id, "Оберіть одне з налаштувань:", reply_markup=model_settings_kb)
  elif message.text == "🕹\nОбрати модель":
    await Form.in_choose_model_ukr.set()
    await bot.send_message(message.from_user.id, f"Ваша поточна модель - це {get_model(message.from_user.id)}.", reply_markup=return_kb)
    await bot.send_message(message.from_user.id, f"Оберіть одну з доступних моделей:", reply_markup=model_kb)
  else:
### check if the user's token balance is less than the token limit ###
    user_id = message.from_user.id
    if get_text_davinci_003_settings(user_id) is None:
      await bot.send_message(message.from_user.id, "Помилка: Ви не зареєстровані.")
      return
    tokens, max_length, temperature = get_text_davinci_003_settings(user_id)
    print(get_text_davinci_003_settings(user_id))
    if tokens < max_length:
      await bot.send_message(message.from_user.id, f"Недостатня кількість токенів на рахунку: {tokens}")
      return
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=(f"{message.text}\n"),
        max_tokens=max_length,
        n = 1,
        stop=None,
        temperature=temperature,
    )
    generated_text = response["choices"][0]["text"]
    print(generated_text)
    await bot.send_message(message.from_user.id, response["choices"][0]["text"])
    num_tokens_used = response["usage"]["total_tokens"]
    print('num_tokens_used:' ,num_tokens_used)
    subtract_tokens(user_id, num_tokens_used)
    await bot.send_message(message.from_user.id, f"Баланс токенів: {tokens-num_tokens_used}")

                ### In_prompt_settings handler ###
#@dp.message_handler(state=Form.in_model_settings_ukr)
async def in_prompt_settings_ukr(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '\u2B05':
    await Form.in_text_davinci_003_ukr.set()
    await bot.send_message(message.from_user.id, "Ви можете продовжувати спілкування.", reply_markup=in_text_davinci_003_kb)
  elif message.text == 'Максимальна довжина':
    await Form.in_max_length_ukr.set()
    current_max_length = get_max_length(user_id)
    await bot.send_message(message.from_user.id, f"Ваша поточна Максимальна Довжина складає: {current_max_length}.\nБудь ласка, введіть необхідну довжину:", reply_markup=max_length_kb)
  elif message.text == 'Температура':
    await Form.in_temperature_ukr.set()
    current_temperature = get_temperature(user_id)
    await bot.send_message(message.from_user.id, f"Ваша поточна Температура становить: {current_temperature}.", reply_markup=temperature_replykeyboard)
    await bot.send_message(message.from_user.id, "Будь ласка, введіть необхідне значення:", reply_markup=temperature_inlinekeyboard)

                  ### Processing Max_length ###
#@dp.message_handler(state=Form.in_max_length_ukr)
async def in_max_length_ukr(message: Message, state: FSMContext):
  try:
    max_length = int(message.text)
    if max_length > 4097:
      await bot.send_message(message.from_user.id, "Максимальна довжина для цієї моделі становить 4097 токенів, які розподіляються між вхідним текстом та результатом.")
    elif  max_length < 1:
      await bot.send_message(message.from_user.id, "Максимальна довжина не може бути меншою за 1.")
    else:
      update_max_length(message.from_user.id, max_length)
      await Form.in_model_settings_ukr.set()
      await bot.send_message(message.from_user.id, f"Максимальну довжину було змінено на {max_length}.", reply_markup=model_settings_kb)
  except ValueError:
    if message.text == '\u2B05':
      await Form.in_model_settings_ukr.set()
      await bot.send_message(message.from_user.id, "Оберіть одне з налаштувань:", reply_markup=model_settings_kb)
    elif message.text == "\uFF1F":
      user_id = message.from_user.id
      current_max_length = get_max_length(user_id)
      await bot.send_message(message.from_user.id, f"Максимальна довжина - це максимальна кількість токенів, що можуть бути згенеровані за раз. Один токен відповідає приблизно 4 символам для звичайного тексту.\nВи можете використовувати до 4097 токенів, які розподіляються між вхідним текстом та результатом.\n\nВаша поточна Максимальна Довжина складає: {current_max_length}\nБудь ласка, оберіть необхідне вам значення:", reply_markup=max_length_kb)
    else:
      await bot.send_message(message.from_user.id, "Будь ласка, введіть числове значення.")

                     ### In_temperature handler ###
#@dp.callback_query_handler(lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state = Form.in_temperature_ukr)
async def in_temperature_inline_ukr(callback_query: CallbackQuery, state: FSMContext):
  temperature = float(callback_query.data)
  if 0 <= temperature <= 1:
    update_temperature(callback_query.from_user.id, temperature)
    await Form.in_model_settings_ukr.set()
    await bot.send_message(callback_query.from_user.id, f"Температуру було встановлено на рівні: {temperature}.", reply_markup=model_settings_kb)

    
              ### Return button for In_temperature ###
#@dp.message_handler(state=Form.in_temperature_ukr)
async def in_temperature_reply_ukr(message: Message, state: FSMContext):
  try:
    temperature = float(message.text)
    if 0 <= temperature <= 1:
      update_temperature(message.from_user.id, temperature)
      await Form.in_model_settings_ukr.set()
      await bot.send_message(message.from_user.id, f"Температуру було встановлено на рівні {temperature}.", reply_markup=model_settings_kb)
    else:
      raise ValueError
  except ValueError:
    if message.text == "\u2B05":
      await Form.in_model_settings_ukr.set()
      await bot.send_message(message.from_user.id, "Оберіть одне з налаштувань:", reply_markup=model_settings_kb)
    elif message.text == "\uFF1F":
      user_id = message.from_user.id
      current_temperature = get_temperature(user_id)
      await bot.send_message(message.from_user.id, f"Температура контролює креативність та випадковість відповідей, створених лінгвістичною моделлю. Низька температура призведе до більш консервативних та детермінованих відповідей, тоді як вища температура створить більш різноманітні та непередбачувані відповіді. Температуру можна налаштувати в залежності від бажаного рівня креативності та логічної зв'язності для конкретної задачі\n\nВаша поточна Температура становить: {current_temperature}. Будь ласка, оберіть необхідне вам значення:", reply_markup=temperature_inlinekeyboard)
    else:
      await bot.send_message(message.from_user.id, "Температура повинна бути числовим значенням від 0 до 1.", reply_markup=temperature_inlinekeyboard)
    


                           ### In choose model ###
#@dp.callback_query_handler(lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state = Form.in_choose_model_ukr)
async def in_choose_model_inline_ukr(callback_query: CallbackQuery, state: FSMContext):
  model = callback_query.data
  if model == "gpt-3.5-turbo":
    change_model(callback_query.from_user.id, model)
    await Form.in_gpt_turbo_ukr.set()
    await bot.send_message(callback_query.from_user.id, f"Модель було змінено на {model}. Ви можете продовжувати спілкування.", reply_markup=in_gpt_turbo_kb)
  elif model == 'text-davinci-003':
    change_model(callback_query.from_user.id, model)
    await Form.in_text_davinci_003_ukr.set()
    await bot.send_message(callback_query.from_user.id, f"Модель було змінено на {model}. Ви можете продовжувати спілкування.", reply_markup=in_text_davinci_003_kb)


    
#@dp.message_handler(state=Form.in_choose_model_ukr)
async def in_choose_model_reply_ukr(message: Message, state: FSMContext):
  current_model = get_model(message.from_user.id)
  if message.text == '\u2B05':
    if current_model == "gpt-3.5-turbo":
      chat_keyboard = in_gpt_turbo_kb
      await Form.in_gpt_turbo_ukr.set()
    elif current_model == "text-davinci-003":
      chat_keyboard = in_text_davinci_003_kb
      await Form.in_text_davinci_003_ukr.set()
    await bot.send_message(message.from_user.id, "Вітаю у чаті. Сформулюйте своє питання і відправте мені. Будьте уважні до кількості токенів, які є на вашому рахунку.", reply_markup=chat_keyboard)
  elif message.text == '\uFF1F':
    await bot.send_message(message.from_user.id, "Моделі GPT-3.5 можуть розуміти та генерувати натуральну мову або код.\n\n🤖  gpt-3.5-turbo - Найпотужніша модель GPT-3.5 та оптимізована для чатів за 1/10 від вартості text-davinci-003.\n\n🤖  text-davinci-003 - Може виконувать будь яке лінгвістичне завдання та надає можливість контролювати Максимальну довжину та Температуру.", reply_markup=return_kb)
    
  
  
    
    


        
    


  

#@dp.message_handler(commands=['/Create_content'])
async def command_create_content_ukr(message: Message):
  await bot.send_message(message.from_user.id, 'Choose one of the provided publishing styles or click the button "Your content"', reply_markup=choose_content_type_kb)

#@dp.message_handler(commands=['/Generate_a_picture'])
async def generate_a_picture_ukr(message: Message):
  await bot.send_message(message.from_user.id, 'Опишіть, що ви хочете згенерувати, або скористайтеся нашим посібником ефективного промптування, щоб отримати максимальний результат.')


  

                       ### Registering Handlers ###
def register_handlers_client_UKR(dp : Dispatcher):
  dp.register_message_handler(chat_with_sparkie_ukr, Text(equals='💬 Чат зі Sparkie'))
  dp.register_message_handler(in_gpt_turbo_ukr, state=Form.in_gpt_turbo_ukr)
  dp.register_message_handler(in_text_davinci_003_ukr, state=Form.in_text_davinci_003_ukr)
  dp.register_message_handler(in_prompt_settings_ukr, state=Form.in_model_settings_ukr)
  dp.register_message_handler(in_max_length_ukr, state=Form.in_max_length_ukr)
  dp.register_callback_query_handler(in_temperature_inline_ukr, lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state=Form.in_temperature_ukr)
  dp.register_message_handler(in_temperature_reply_ukr, state=Form.in_temperature_ukr)
  dp.register_callback_query_handler(in_choose_model_inline_ukr, lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state=Form.in_choose_model_ukr)
  dp.register_message_handler(in_choose_model_reply_ukr, state=Form.in_choose_model_ukr)
  dp.register_message_handler(generate_a_picture_ukr, Text(equals='🖼️ Згенерувати зображення'))
  #dp.register_message_handler(command_create_content_ukr, Text(equals='Create content'))
  


      ### callback query handler to handle the callback data sent by the inline buttons when "Create content" is pressed ###
  
@dp.callback_query_handler(lambda c: c.data in ["post", "article", "story", "business letter", "commercial", "your content"])
async def process_create_content_ukr(callback_query: CallbackQuery):
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


