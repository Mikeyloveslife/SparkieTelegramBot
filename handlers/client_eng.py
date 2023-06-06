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


from data_base.get_sqlite import *

class Form(StatesGroup):
  in_gpt_turbo = State()
  in_text_davinci_003 = State()
  in_model_settings = State()
  in_choose_model = State()
  in_max_length = State()
  in_temperature = State()
    
 


                ### Chat with Sparkie ###
#@dp.message_handler(Text(equals='Chat with Sparkie'))
async def chat_with_sparkie_eng(message: Message):
  if get_model(message.from_user.id) == 'gpt-3.5-turbo':
    await Form.in_gpt_turbo.set()
    await bot.send_message(message.from_user.id, "Hello you can ask me anything you want. Mind the number of tokens you have in balance.", reply_markup=in_gpt_turbo_kb)
  if get_model(message.from_user.id) == 'text-davinci-003':
    await Form.in_text_davinci_003.set()
    await bot.send_message(message.from_user.id, "Hello you can ask me anything you want. Mind the number of tokens you have in balance.", reply_markup=in_text_davinci_003_kb)


                   ### Chat with Sparkie in_gpt_turbo ###
#@dp.message_handler(state=Form.in_gpt_turbo)
async def in_gpt_turbo_eng(message: Message, state: FSMContext):
  if message.text == '\u2B05':
    await state.finish()
    await bot.send_message(message.from_user.id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif message.text == "🕹\nChoose model":
    await Form.in_choose_model.set()
    await bot.send_message(message.from_user.id, f"Your current model is {get_model(message.from_user.id)}.", reply_markup=return_kb)
    await bot.send_message(message.from_user.id, "Choose one of the supported models:", reply_markup=model_kb)
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
    await bot.send_message(message.from_user.id, f"Token balance: {tokens-num_tokens_used}")
    

               ### Chat with Sparkie in_text_davinci_003 ###
#@dp.message_handler(state=Form.in_text_davinci_003)
async def in_text_davinci_003_eng(message: Message, state: FSMContext):
  if message.text == '\u2B05':
    await state.finish()
    await bot.send_message(message.from_user.id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif message.text == "⚙️\nModel settings":
    await Form.in_model_settings.set()
    await bot.send_message(message.from_user.id, "Select one of the settings:", reply_markup=model_settings_kb)
  elif message.text == "🕹\nChoose model":
    await Form.in_choose_model.set()
    await bot.send_message(message.from_user.id, f"Your current model is {get_model(message.from_user.id)}.", reply_markup=return_kb)
    await bot.send_message(message.from_user.id, "Choose one of the supported models:", reply_markup=model_kb)
  else:
### check if the user's token balance is less than the token limit ###
    user_id = message.from_user.id
    if get_text_davinci_003_settings(user_id) is None:
      await bot.send_message(message.from_user.id, "Error: You are not registered.")
      return
    tokens, max_length, temperature = get_text_davinci_003_settings(user_id)
    print(get_text_davinci_003_settings(user_id))
    if tokens < max_length:
      await bot.send_message(message.from_user.id, f"Insufficient token balance: {tokens}")
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
    await bot.send_message(message.from_user.id, f"Token balance: {tokens-num_tokens_used}")

                ### In_prompt_settings handler ###
#@dp.message_handler(state=Form.in_model_settings)
async def in_prompt_settings_eng(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '\u2B05':
    await Form.in_text_davinci_003.set()
    await bot.send_message(message.from_user.id, "You can keep chatting.", reply_markup=in_text_davinci_003_kb)
  elif message.text == 'Maximum length':
    await Form.in_max_length.set()
    current_max_length = get_max_length(user_id)
    await bot.send_message(message.from_user.id, f"Your current maximum length is {current_max_length}.\nPlease enter your desired length:", reply_markup=max_length_kb)
  elif message.text == 'Temperature':
    await Form.in_temperature.set()
    current_temperature = get_temperature(user_id)
    await bot.send_message(message.from_user.id, f"Your current Temperature is {current_temperature}.", reply_markup=temperature_replykeyboard)
    await bot.send_message(message.from_user.id, "Please enter the desired value:", reply_markup=temperature_inlinekeyboard)

                  ### Processing Max_length ###
#@dp.message_handler(state=Form.in_max_length)
async def in_max_length_eng(message: Message, state: FSMContext):
  try:
    max_length = int(message.text)
    if max_length > 4097:
      await bot.send_message(message.from_user.id, "Max length for this model is 4097 tokens shared between prompt and completion.")
    elif  max_length < 1:
      await bot.send_message(message.from_user.id, "Maximum length cannot be less than 1.")
    else:
      update_max_length(message.from_user.id, max_length)
      await Form.in_model_settings.set()
      await bot.send_message(message.from_user.id, f"Maximum length has been updated to {max_length}.", reply_markup=model_settings_kb)
  except ValueError:
    if message.text == '\u2B05':
      await Form.in_model_settings.set()
      await bot.send_message(message.from_user.id, "Select one of the settings", reply_markup=model_settings_kb)
    elif message.text == "\uFF1F":
      user_id = message.from_user.id
      current_max_length = get_max_length(user_id)
      await bot.send_message(message.from_user.id, f"Maximum length is the maximum number of tokens to generate. One token is roughly 4 characters for normal English text.\nYou can use up to 4097 tokens shared between prompt and completion.\n\nYour current Maximum length is {current_max_length}\nPlease enter your desired Maximum length.", reply_markup=max_length_kb)
    else:
      await bot.send_message(message.from_user.id, "Please input a numerical value.")
  



                     ### In_temperature handler ###
#@dp.callback_query_handler(lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state = Form.in_temperature)
async def in_temperature_inline_eng(callback_query: CallbackQuery, state: FSMContext):
  temperature = float(callback_query.data)
  if 0 <= temperature <= 1:
    update_temperature(callback_query.from_user.id, temperature)
    await Form.in_model_settings.set()
    await bot.send_message(callback_query.from_user.id, f"Temperature has been set to {temperature}.", reply_markup=model_settings_kb)

    
              ### Return button for In_temperature ###
#@dp.message_handler(state=Form.in_temperature)
async def in_temperature_reply_eng(message: Message, state: FSMContext):
  try:
    temperature = float(message.text)
    if 0 <= temperature <= 1:
      update_temperature(message.from_user.id, temperature)
      await Form.in_model_settings.set()
      await bot.send_message(message.from_user.id, f"Temperature has been set to {temperature}.", reply_markup=model_settings_kb)
    else:
      raise ValueError
  except ValueError:
    if message.text == "\u2B05":
      await Form.in_model_settings.set()
      await bot.send_message(message.from_user.id, "Select one of the settings:", reply_markup=model_settings_kb)
    elif message.text == "\uFF1F":
      user_id = message.from_user.id
      current_temperature = get_temperature(user_id)
      await bot.send_message(message.from_user.id, f"Temperature controls the creativity and randomness of the responses generated by a language model. A low temperature will result in more conservative and deterministic responses, while a higher temperature will produce more varied and unpredictable responses. The temperature can be adjusted depending on the desired level of creativity and coherence for a specific task.\n\nYour current Temperature is {current_temperature}. Please choose the desired value:", reply_markup=temperature_inlinekeyboard)
    else:
      await bot.send_message(message.from_user.id, "The temperature setting should be a numerical value between 0 and 1.", reply_markup=temperature_inlinekeyboard)
    
    


                 ### In choose model ###
#@dp.callback_query_handler(lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state = Form.in_choose_model)
async def in_choose_model_inline_eng(callback_query: CallbackQuery, state: FSMContext):
  model = callback_query.data
  if model == "gpt-3.5-turbo":
    change_model(callback_query.from_user.id, model)
    await Form.in_gpt_turbo.set()
    await bot.send_message(callback_query.from_user.id, f"The model has been changed to {model}. You can keep chatting.", reply_markup=in_gpt_turbo_kb)
  elif model == 'text-davinci-003':
    change_model(callback_query.from_user.id, model)
    await Form.in_text_davinci_003.set()
    await bot.send_message(callback_query.from_user.id, f"The model has been changed to {model}. You can keep chatting.", reply_markup=in_text_davinci_003_kb)


    
#@dp.message_handler(state=Form.in_choose_model)
async def in_choose_model_reply_eng(message: Message, state: FSMContext):
  current_model = get_model(message.from_user.id)
  if message.text == '\u2B05':
    if current_model == "gpt-3.5-turbo":
      chat_keyboard = in_gpt_turbo_kb
      await Form.in_gpt_turbo.set()
    elif current_model == "text-davinci-003":
      chat_keyboard = in_text_davinci_003_kb
      await Form.in_text_davinci_003.set()
    await bot.send_message(message.from_user.id, "Hello you can ask me anything you want. Mind the number of tokens you have in balance.", reply_markup=chat_keyboard)
  elif message.text == '\uFF1F':
    await bot.send_message(message.from_user.id, "GPT-3.5 models can understand and generate natural language or code.\n\n🤖  gpt-3.5-turbo - Most capable GPT-3.5 model and optimized for chat at 1/10th the cost of text-davinci-003.\n\n🤖  text-davinci-003 - Can do any language task and gives control over Maximum length and Temperature used in prompts.", reply_markup=return_kb)
    
  
  
    
    


        
    


  

#@dp.message_handler(commands=['/Create_content'])
async def command_create_content_eng(message: Message):
  await bot.send_message(message.from_user.id, 'Choose one of the provided publishing styles or click the button "Your content"', reply_markup=choose_content_type_kb)



  

               ### Registering Handlers ###
def register_handlers_client_ENG(dp : Dispatcher):
  dp.register_message_handler(chat_with_sparkie_eng, Text(equals='💬 Chat with Sparkie'))
  dp.register_message_handler(in_gpt_turbo_eng, state=Form.in_gpt_turbo)
  dp.register_message_handler(in_text_davinci_003_eng, state=Form.in_text_davinci_003)
  dp.register_message_handler(in_prompt_settings_eng, state=Form.in_model_settings)
  dp.register_message_handler(in_max_length_eng, state=Form.in_max_length)
  dp.register_callback_query_handler(in_temperature_inline_eng, lambda c: c.data in ["0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], state=Form.in_temperature)
  dp.register_message_handler(in_temperature_reply_eng, state=Form.in_temperature)
  dp.register_callback_query_handler(in_choose_model_inline_eng, lambda c: c.data in ["gpt-3.5-turbo", "text-davinci-003"], state=Form.in_choose_model)
  dp.register_message_handler(in_choose_model_reply_eng, state=Form.in_choose_model)
  # dp.register_message_handler(generate_a_picture_eng, Text(equals='🖼️ Generate a picture'))
  #dp.register_message_handler(command_create_content_eng, Text(equals='Create content'))
  


      ### callback query handler to handle the callback data sent by the inline buttons when "Create content" is pressed ###
  
@dp.callback_query_handler(lambda c: c.data in ["post", "article", "story", "business letter", "commercial", "your content"])
async def process_create_content_eng(callback_query: CallbackQuery):
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


