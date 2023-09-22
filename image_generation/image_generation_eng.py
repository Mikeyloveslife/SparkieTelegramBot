import os
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

from create_bot import dp, bot
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.keyboards_eng import menu_kb, image_generation_inline_kb, size_inline_kb, size_reply_kb

from data_base.sqlite_db import Database, All_states
db = Database('user_settings.db')


# class Form(StatesGroup):
  #in_generate_image = State()
  # in_generate_image_variation = State()
  # in_image_size = State()



from io import BytesIO
from PIL import Image


@dp.message_handler(text="🖼️ Image generation")
async def image_generation_eng(message: Message):
  await bot.send_message(message.from_user.id, 'Choose if you want to create a new image or a variation out of existing image:', reply_markup=image_generation_inline_kb)


@dp.callback_query_handler(lambda c: c.data in ["generate image", "generate image variation"])
async def choose_img_gen_endpoint(callback_query: CallbackQuery, state: FSMContext):
  user_id = callback_query.from_user.id
  button_text = callback_query.data
  if button_text == "generate image":
    await All_states.in_generate_image.set()
  elif button_text == "generate image variation":
    await All_states.in_generate_image_variation.set()
    
  await bot.send_message(user_id, 'Choose image resolution:', reply_markup=size_inline_kb)

@dp.callback_query_handler(lambda c: c.data in ["256x256", "512x512", "1024x1024"], state=[All_states.in_generate_image, All_states.in_generate_image_variation])
async def choose_img_size(callback_query: CallbackQuery, state: FSMContext):
  user_id = callback_query.from_user.id
  img_size = callback_query.data
  db.update_param(user_id, ("img_size", img_size))
  current_state = await state.get_state()
  if img_size and current_state == All_states.in_generate_image.state:
    await bot.send_message(user_id, 'Provide a text description of the desired image within the length of 1000 characters:', reply_markup=size_reply_kb)
  elif img_size and current_state == All_states.in_generate_image_variation.state:
    await bot.send_message(user_id, 'Send a square PNG image less than 4MB in size:', reply_markup=size_reply_kb)

#@dp.message_handler(state=Form.in_generate_image)
async def create_image(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '⬅️':
    await state.finish()
    await bot.send_message(user_id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif message.text == "Image size":
    await bot.send_message(user_id, "Choose image resolution:", reply_markup=size_inline_kb)
  else:
    try:
      # create_image = openai.Image.create(
      # prompt=f"{message.text}",
      # n=1,
      # size=db.get_img_size(user_id)[0])
      # image = create_image['data'][0]['url']
      # tokens = db.get_token_balance(user_id)
      # num_tokens_used = db.get_img_size(user_id)[1]
      # print(num_tokens_used)
      # db.subtract_tokens(user_id, num_tokens_used)
      # await bot.send_message(user_id, image, reply_markup=size_reply_kb)
      # await bot.send_message(user_id, f"Token balance: {tokens-num_tokens_used}")
      print("GENERATING AN IMAGE")
    except openai.error.OpenAIError as e:
      await bot.send_message(user_id, e.error["message"])


#@dp.message_handler(content_types=['photo', 'text'], state=All_states.in_generate_image_variation)
async def create_image_variation(message: Message, state: FSMContext):
  user_id = message.from_user.id
  if message.text == '⬅️':
    await state.finish()
    await bot.send_message(user_id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif message.text == "Image size":
    await bot.send_message(user_id, "Choose image resolution:", reply_markup=size_inline_kb)
  else:
    print("HEY1")
    ###
    photo = message.photo[-1] 
    file_id = photo.file_id
    file_path = f"photos/{photo.file_id}.jpg"
    await photo.download(destination_file=file_path)
    print("HEY2")
    ###
    image = Image.open(file_path)
    width, height = 256, 256
    image = image.resize((width, height))
    image = image.convert("RGB")
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    byte_array = byte_stream.getvalue()
    print("HEY3")
    try:
      create_image_variation = openai.Image.create_variation(
      image=byte_array,
      n=1,
      size=db.get_img_size(user_id)[0])
      variation_url = create_image_variation['data'][0]['url']
      await bot.send_photo(user_id, photo=variation_url, caption='Here is the variation of the provided image.')
      print("HEY4")
      tokens = db.get_token_balance(user_id)
      num_tokens_used = db.get_img_size(user_id)[1]
      db.subtract_tokens(user_id, num_tokens_used)
      await bot.send_message(user_id, f"Token balance: {tokens-num_tokens_used}")
    except openai.error.OpenAIError as e:
      await bot.send_message(user_id, e.error["message"])







    