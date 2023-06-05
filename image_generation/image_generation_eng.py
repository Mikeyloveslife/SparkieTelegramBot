import os
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

from create_bot import dp, bot
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base.sqlite_db import get_token_balance
from keyboards.keyboards_eng import menu_kb, image_generation_inline_kb, return_kb

class Form(StatesGroup):
  in_create_image = State()
  in_create_image_variation = State()



@dp.message_handler(Text(equals='🖼️ Image generation'))
async def image_generation_eng(message: Message):
  await bot.send_message(message.from_user.id, 'Choose if you want to create a new image or an image variation out of existing picture:', reply_markup=image_generation_inline_kb)


@dp.callback_query_handler(lambda c: c.data in ["create image", "create image variation"])
async def choose_image_format(callback_query: CallbackQuery, state: FSMContext):
  button_text = callback_query.data
  if button_text == "create image":
    await Form.in_create_image.set()
    await bot.send_message(callback_query.from_user.id, 'Provide a text description of the desired image within the length of 1000 characters:', reply_markup=return_kb)
  elif button_text == "create image variation":
    await Form.in_create_image_variation.set()
    await bot.send_message(callback_query.from_user.id, 'Send an image to use as the basis for the variation. Must be a valid PNG file, less than 4MB, and square:', reply_markup=return_kb)

@dp.message_handler(state=Form.in_create_image)
async def create_image(message: Message, state: FSMContext):
  if message.text == '\u2B05':
    await state.finish()
    await bot.send_message(message.from_user.id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif message.text == "\uFF1F":
    await bot.send_message(message.from_user.id, "Model under the hood is DALL·E, an AI system that can create realistic images and art from a description in natural language. It has the ability, given a prommpt, to create a new image:", reply_markup=return_kb)
  else:
    create_image = openai.Image.create(
    prompt=f"{message.text}\n",
    n=1,
    size="1024x1024")
    image = create_image['data'][0]['url']
    await bot.send_message(message.from_user.id, image)


@dp.message_handler(content_types=['photo'], state=Form.in_create_image_variation)
async def create_image_variation(message: Message, state: FSMContext):
    if message.caption == '\u2B05':
        await state.finish()
        await bot.send_message(message.from_user.id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
    elif message.caption == "\uFF1F":
        await bot.send_message(message.from_user.id, "Model under the hood is DALL·E, an AI system that can create realistic images and art from a description in natural language. It has the ability to create variations of a user provided image:", reply_markup=return_kb)
    else:
        print("Buba here")
        image = await message.photo[-1]
        file_size = os.path.getsize(image.name)
        if file_size > 4 * 1024 * 1024:
          await bot.send_message(message.from_user.id, "The file is too large. Please send an image that is less than 4 MB.", reply_markup=return_kb)
        else:
          print(image.name)
          with open(f"{image.name}", "rb") as img_file:
              create_image_variation = openai.Image.create_variation(
                  image=img_file,
                  n=1,
                  size="1024x1024")
              variation_url = create_image_variation['data'][0]['url']
          print("Buba here")
          await bot.send_photo(message.from_user.id, photo=variation_url, caption='Here is the variation of the provided image.')
          print("Buba here")




    