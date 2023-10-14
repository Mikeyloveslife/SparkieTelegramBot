import os
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

from create_bot import dp, bot
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext


from keyboards.keyboards_eng import menu_kb, in_text_davinci_003_kb, model_settings_kb, max_length_kb, temperature_replykeyboard, temperature_inlinekeyboard, language_kb, model_kb, return_kb, in_gpt_turbo_kb

from keyboards import keyboards_eng, keyboards_ukr, keyboards_ru

from data_base.sqlite_db import Database, All_states


db = Database('user_settings.db')

                    ### MENU HANDLER ###
from image_generation.image_generation_eng import image_generation_eng
from payments.payments_eng import check_balance     
     

          ### CREATE COMPLETION, SUM COMPLETION ###
def create_completion(chat_history, message):
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": f"You are a helpful assistant called Sparky. Here is the history of your chat with the user '{chat_history}'. Use the chat history only if it's related to the new prompt from a user"},
      {"role": "user", "content": f"{message}"}])
  return completion

def sum_completion(chat_history, new_prompt, new_response):
  sum_completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": f"You are an assistant who summurizes the most important information from the chat. The summurization should not exceed 500 tokens. The contents to summurize include: chat history, new prompt, new response. Here they are consecutively: 1 - '{chat_history}' 2 - '{new_prompt}'' 3 - '{new_response}'"}])
  return sum_completion

# sum_completion = sum_completion(chat_history, message.text, completion["choices"][0]["message"]["content"])
# completion = create_completion(chat_history, message.text)
  

                  ### CHAT WITH SPARKY ###
#@dp.message_handler(Text(equals='Chat with Sparkie'))
async def chat_with_sparkie_eng(message: Message):
  user_id = message.from_user.id
  model = db.get_param(user_id, ("model",))
  if model == 'gpt-3.5-turbo':
    await All_states.in_gpt_turbo.set()
    reply_markup = in_gpt_turbo_kb
  elif model == 'text-davinci-003':
    await All_states.in_text_davinci_003.set()
    reply_markup = in_text_davinci_003_kb
  await bot.send_message(user_id, "Hello you can ask me anything you want. Mind the number of tokens you have in balance.", reply_markup=reply_markup)


          ### CHAT WITH SPARKY in_gpt_turbo handler ###
#@dp.message_handler(state=Form.in_gpt_turbo)
async def in_gpt_turbo_eng(message: Message, state: FSMContext):
  user_id = message.from_user.id
  user_message = message.text
  if user_message == '⬅️':
    await state.finish()
    await bot.send_message(user_id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif user_message == "🕹\nChoose model":
    await All_states.in_choose_model.set()
    model = db.get_param(user_id, ("model",))
    await bot.send_message(user_id, f"Your current model is {model}.", reply_markup=return_kb)
    await bot.send_message(user_id, "Choose one of the supported models:", reply_markup=model_kb)
  else:
    try:
    #   chat_history = db.get_param(user_id, ("chat_history",))
    #   completion = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=[
    #   {"role": "system", "content": f"You are a helpful assistant called Sparky. Here is the history of your chat with the user '{chat_history}'. Use the chat history only if it's related to the new prompt from a user"},
    #   {"role": "user", "content": f"{message}"}])
    #   new_response = completion["choices"][0]["message"]["content"]
    #   sum_completion = openai.ChatCompletion.create(
    #   model="gpt-3.5-turbo",
    #   messages=[
    #   {"role": "system", "content": f"You are an assistant who summurizes the most important information from the chat. The summurization should not exceed 300 tokens, and you should keep it as concise as possible. The contents to summurize include: chat history, new prompt, new response. Here they are consecutively: 1 - '{chat_history}' 2 - '{user_message}'' 3 - '{new_response}'"}])
    #   sum = sum_completion["choices"][0]["message"]["content"]
    #   print(sum)
    #   await bot.send_message(user_id, new_response)
    #   db.update_param(user_id, ("chat_history", sum))
    #   tokens = db.get_param(user_id, ("tokens",))
    #   num_tokens_used = completion["usage"]["total_tokens"] + sum_completion["usage"]["total_tokens"]
    #   print('\nnum_tokens_used:', num_tokens_used)
    #   db.subtract_tokens(user_id, num_tokens_used)
    #   await bot.send_message(user_id, f"Token balance: {tokens-num_tokens_used}")
        print("IN GPT-TURBO MA MAN")
    except Exception as e:
      await bot.send_message(user_id, "An error occurred during the model interaction. Please try again later.")
      print(e)

    

            ### CHAT WITH SPARKY in_text_davinci_003 ###
#@dp.message_handler(state=Form.in_text_davinci_003)
async def in_text_davinci_003_eng(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '⬅️':
    await state.finish()
    await bot.send_message(user_id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif message.text == "⚙️\nModel settings":
    await All_states.in_model_settings.set()
    await bot.send_message(user_id, "Select one of the settings:", reply_markup=model_settings_kb)
  elif message.text == "🕹\nChoose model":
    await All_states.in_choose_model.set()
    model = db.get_param(user_id, ("model",))
    await bot.send_message(user_id, f"Your current model is {model}.", reply_markup=return_kb)
    await bot.send_message(user_id, "Choose one of the supported models:\n\nGPT-3.5 models can understand and generate natural language or code.\n\n1.  gpt-3.5-turbo - Most capable GPT-3.5 model and optimized for chat at 1/10th the cost of text-davinci-003.\n\n2.  text-davinci-003 - Can do any language task and gives control over Maximum length and Temperature used in prompts.", reply_markup=model_kb)
  else:
    try:
    # check if a user's token balance is less than the max length
      tokens, max_length, temperature = db.get_param(user_id, ("tokens", "max_length", "temperature"))
      print(tokens, max_length, temperature)
      if tokens < max_length:
        await bot.send_message(user_id, f"Insufficient token balance: {tokens}")
        return
      completion = openai.Completion.create(
      engine="text-davinci-003",
      prompt=(f"{message.text}"),
      max_tokens=max_length,
      n = 1,
      stop=None,
      temperature=temperature,
      )
      await bot.send_message(user_id, completion["choices"][0]["text"])
      num_tokens_used = completion["usage"]["total_tokens"]
      print('num_tokens_used:' ,num_tokens_used)
      db.subtract_tokens(user_id, num_tokens_used)
      await bot.send_message(user_id, f"Token balance: {tokens-num_tokens_used}")
    except Exception as e:
      await bot.send_message(user_id, "An error occurred during the model interaction. Please try again later.")
      print(e)

                ### IN PROMPT SETTINGS HANDLER ###
#@dp.message_handler(state=All_states.in_model_settings)
async def in_prompt_settings_eng(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '⬅️':
    await All_states.in_text_davinci_003.set()
    await bot.send_message(user_id, "You can keep chatting.", reply_markup=in_text_davinci_003_kb)
  elif message.text == 'Maximum length':
    await All_states.in_max_length.set()
    current_max_length = db.get_param(user_id, ("max_length",))
    await bot.send_message(user_id, f"Maximum length is the maximum number of tokens to generate. One token is roughly 4 characters for normal English text.\nYou can use up to 4097 tokens shared between prompt and completion.\n\nYour current Maximum length is {current_max_length}.\nPlease specify the maximum length you need.", reply_markup=max_length_kb)
  elif message.text == 'Temperature':
    await All_states.in_temperature.set()
    current_temperature = db.get_param(user_id, ("temperature",))
    await bot.send_message(user_id, f"Your current Temperature is {current_temperature}.", reply_markup=temperature_replykeyboard)
    await bot.send_message(user_id, "Please enter the desired value:", reply_markup=temperature_inlinekeyboard)

                  ### MAX LENGTH HANDLER ###
#@dp.message_handler(state=All_states.in_max_length)
async def in_max_length_eng(message: Message, state: FSMContext):
  user_id = message.from_user.id
  try:
    max_length = int(message.text)
    if max_length > 4097:
      await bot.send_message(user_id, "Max length for this model is 4097 tokens shared between prompt and completion.")
    elif  max_length < 1:
      await bot.send_message(user_id, "Maximum length cannot be less than 1.")
    else:
      db.update_param(user_id, ("max_length", max_length))
      await All_states.in_model_settings.set()
      await bot.send_message(user_id, f"Maximum length has been updated to {max_length}.", reply_markup=model_settings_kb)
  except ValueError:
    if message.text == '⬅️':
      await All_states.in_model_settings.set()
      await bot.send_message(user_id, "Select one of the settings", reply_markup=model_settings_kb)
    elif message.text == "�":
      current_max_length = db.get_param(user_id, ("max_length",))
      await bot.send_message(user_id, f"Maximum length is the maximum number of tokens to generate. One token is roughly 4 characters for normal English text.\nYou can use up to 4097 tokens shared between prompt and completion.\n\nYour current Maximum length is {current_max_length}.\nPlease specify the maximum length you need.", reply_markup=max_length_kb)
    else:
      await bot.send_message(user_id, "Please input an integer.")
  



              ### IN TEMPERATURE INLINE HANDLER ###
#@dp.callback_query_handler(lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state = All_states.in_temperature)
async def in_temperature_inline_eng(callback_query: CallbackQuery, state: FSMContext):
  user_id = callback_query.from_user.id
  temperature = float(callback_query.data)
  if 0 <= temperature <= 1:
    db.update_param(user_id, ("temperature", temperature))
    await All_states.in_model_settings.set()
    await bot.send_message(user_id, f"Temperature has been set to {temperature}.", reply_markup=model_settings_kb)

    
              ### IN TEMPERATURE REPLY HANDLER ###
#@dp.message_handler(state=All_states.in_temperature)
async def in_temperature_reply_eng(message: Message, state: FSMContext):
  user_id = message.from_user.id
  try:
    temperature = float(message.text)
    if 0 <= temperature <= 1:
      db.update_param(user_id, ("temperature", temperature))
      await All_states.in_model_settings.set()
      await bot.send_message(user_id, f"Temperature has been set to {temperature}.", reply_markup=model_settings_kb)
    else:
      raise ValueError
  except ValueError:
    if message.text == "⬅️":
      await All_states.in_model_settings.set()
      await bot.send_message(user_id, "Select one of the settings:", reply_markup=model_settings_kb)
    elif message.text == "�":
      current_temperature = db.get_param(user_id, ("temperature",))
      await bot.send_message(user_id, f"Temperature controls the creativity and randomness of the responses generated by a language model. A low temperature will result in more conservative and deterministic responses, while a higher temperature will produce more varied and unpredictable responses. The temperature can be adjusted depending on the desired level of creativity and coherence for a specific task.\n\nYour current Temperature is {current_temperature}. Please choose the desired value:", reply_markup=temperature_inlinekeyboard)
    else:
      await bot.send_message(user_id, "The temperature setting should be a numerical value between 0 and 1.", reply_markup=temperature_inlinekeyboard)
    
    


            ### IN CHOOSE MODEL INLINE KEYBOARD ###
#@dp.callback_query_handler(lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state = All_states.in_choose_model)
async def in_choose_model_inline_eng(callback_query: CallbackQuery, state: FSMContext):
  user_id = callback_query.from_user.id
  model = callback_query.data
  reply_markup = None
  if model == "gpt-3.5-turbo":
    # user_lang = db.get_param(user_id, ("language",))
    # print(user_lang, "MIRACLE")
    db.update_param(user_id, ("model", model))
    await All_states.in_gpt_turbo.set()
    reply_markup=in_gpt_turbo_kb
  elif model == 'text-davinci-003':
    db.update_param(user_id, ("model", model))
    await All_states.in_text_davinci_003.set()
    reply_markup=in_text_davinci_003_kb
  await bot.send_message(user_id, f"The model has been changed to {model}. You can keep chatting.", reply_markup=reply_markup)


          ### IN CHOOSE MODEL REPLY KEYBOARD ###
#@dp.message_handler(state=All_states.in_choose_model)
async def in_choose_model_reply_eng(message: Message, state: FSMContext):
  user_id = message.from_user.id
  current_model = db.get_param(user_id, ("model",))
  if message.text == '⬅️':
    if current_model == "gpt-3.5-turbo":
      chat_keyboard = in_gpt_turbo_kb
      await All_states.in_gpt_turbo.set()
    elif current_model == "text-davinci-003":
      chat_keyboard = in_text_davinci_003_kb
      await All_states.in_text_davinci_003.set()
    await bot.send_message(user_id, "Hello you can ask me anything you want. Mind the number of tokens you have in balance.", reply_markup=chat_keyboard)
  elif message.text == '�':
    await bot.send_message(user_id, "GPT-3.5 models can understand and generate natural language or code.\n\n1.  gpt-3.5-turbo - Most capable GPT-3.5 model and optimized for chat at 1/10th the cost of text-davinci-003.\n\n2.  text-davinci-003 - Can do any language task and gives control over Maximum length and Temperature used in prompts.", reply_markup=return_kb)



                    #### CHOOSE LANGUAGE ###
@dp.message_handler(text='🌐')
async def choose_lang_reply(message: Message):
  user_id = message.chat.id
  user_lang = db.get_param(user_id, ("language",))
  
  language_messages = {
    'ENG': ("Please choose your preferred language:", keyboards_eng.language_kb),
    'UKR': ("Будь ласка, оберіть вашу мову:", keyboards_ukr.language_kb),
    'RU': ("Пожалуйста, выберите ваш язык:", keyboards_ru.language_kb)
}
  
  if user_lang in language_messages:
    message_text, reply_markup = language_messages[user_lang]
  else:
    message_text, reply_markup = language_messages['ENG']

  await bot.send_message(user_id, message_text, reply_markup=reply_markup)


              ### PROCESS CHOOSE LANGUAGE ###
@dp.callback_query_handler(lambda c: c.data in ["ENG", "UKR", "RU"])
async def choose_lang_inline(callback_query: CallbackQuery):
  # add a user's telegram id to the database and set the token balance to 20000, token limit to 100 and temperature TO 0.5
  user_id = callback_query.from_user.id
  lang = callback_query.data
  print("BUTTON", lang)
  current_lang = db.get_param(user_id, ("language",))
  tokens = 20000
  max_length = 100
  temperature = 0.5
  model = 'gpt-3.5-turbo'
 
  language_messages = {
    'ENG': ("English has been installed.", f"Welcome to Sparky family! We're excited to have you join our community. As a new user, you have been credited with {tokens} tokens to try out our product. We hope you enjoy using our service. Let us know if you have any questions or feedback. Push one of the menu buttons to get started.", keyboards_eng.menu_kb),
    'UKR': ("Встановлено українську мову.", f"Ласкаво просимо до родини Sparky! Ми раді вітати вас в нашій спільноті. Як новому користувачу, вам було нараховано {tokens} токенів, щоб випробувати наш продукт. Ми сподіваємося, що вам сподобається використовувати наш сервіс. Дайте нам знати, якщо у вас є якісь питання або відгуки. Натисніть одну з кнопок меню, щоб почати.", keyboards_ukr.menu_kb),
    'RU': ("Русский язык установлен.", f"Добро пожаловать в семью Sparky! Мы рады, что вы присоединились к нашему сообществу. В качестве нового пользователя вам было начислено {tokens} токенов для тестирования нашего продукта. Мы надеемся, что вам понравится использовать наш сервис. Если у вас есть вопросы или отзывы, пожалуйста, сообщите нам. Нажмите одну из кнопок меню, чтобы начать.", keyboards_ru.menu_kb)
  }
  
  if lang in language_messages:
    message_text, welcome_message, reply_markup = language_messages[lang]

    await bot.send_message(user_id, message_text, reply_markup=reply_markup)
    if current_lang is None:
      db.set_default_user_settings(user_id, tokens, max_length, temperature, model)
      await bot.send_message(user_id, welcome_message, reply_markup=reply_markup)

    db.update_param(user_id, ("language", lang))




                
                ### REGISTERING HANDLERS ###
from image_generation.image_generation_eng import create_image, create_image_variation
           
def register_handlers_client_ENG(dp : Dispatcher):
  dp.register_message_handler(chat_with_sparkie_eng, text='💬 Chat with Sparky')
  dp.register_message_handler(in_gpt_turbo_eng, state=All_states.in_gpt_turbo)
  dp.register_message_handler(in_text_davinci_003_eng, state=All_states.in_text_davinci_003)
  dp.register_message_handler(in_prompt_settings_eng, state=All_states.in_model_settings)
  dp.register_message_handler(in_max_length_eng, state=All_states.in_max_length)
  dp.register_callback_query_handler(in_temperature_inline_eng, lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state=All_states.in_temperature)
  dp.register_message_handler(in_temperature_reply_eng, state=All_states.in_temperature)
  dp.register_callback_query_handler(in_choose_model_inline_eng, lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state=All_states.in_choose_model)
  dp.register_message_handler(in_choose_model_reply_eng, state=All_states.in_choose_model)
  dp.register_message_handler(create_image, state=All_states.in_generate_image)
  dp.register_message_handler(create_image_variation, state=All_states.in_generate_image_variation)
  dp.register_message_handler(check_balance, text="💼\nCheck balance")
  


  


