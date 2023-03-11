from create_bot import dp, bot
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base.sqlite_db import get_token_balance
from keyboards.keyboards_eng import menu_kb, buy_tokens_kb, check_balance_kb, payment_plans_kb, bitcoin_kb

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()


class Form(StatesGroup):
  in_buy_tokens = State()
  in_check_balance = State()
  in_check_balance_buy_tokens = State()

import io
import qrcode


def generate_qr(address, value, bitcoin_price):
    # convert value to Satoshi
    satoshi = int(value * 100000000 / bitcoin_price)
    print(f"$2 is {satoshi} sats")
    # create the payment address string in the format "bitcoin:<address>?amount=<value in Satoshi>"
    payment_address = "bitcoin:" + address + "?amount=" + str(satoshi/100000000)
    # generate the QR code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(payment_address)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # convert the QR code image to a BytesIO object
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return buf


@dp.message_handler(Text(equals='💳\nBuy tokens'))
async def buy_tokens(message: Message, state: FSMContext):
  current_state = await state.get_state()
  if current_state == Form.in_check_balance.state:
    await Form.in_buy_tokens.set()
    user_id = message.from_user.id
    token_balance = get_token_balance(user_id)
    await bot.send_message(message.from_user.id,'Choose one of our payment providers:', reply_markup=bitcoin_kb)
    await bot.send_message(message.from_user.id, f'Your token balance is {token_balance}.', reply_markup=buy_tokens_kb)
    await Form.in_check_balance_buy_tokens.set()
  else:
    await Form.in_buy_tokens.set()
    user_id = message.from_user.id
    token_balance = get_token_balance(user_id)
    await bot.send_message(message.from_user.id,'Choose one of our payment providers:', reply_markup=bitcoin_kb)
    await bot.send_message(message.from_user.id, f'Your token balance is {token_balance}.', reply_markup=buy_tokens_kb)

@dp.message_handler(state=[Form.in_buy_tokens, Form.in_check_balance_buy_tokens])
async def in_buy_tokens(message: Message, state: FSMContext):
  current_state = await state.get_state()
  if current_state == Form.in_buy_tokens.state:
    if message.text == '\u2B05':
      await state.finish()
      await bot.send_message(message.from_user.id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif current_state == Form.in_check_balance_buy_tokens.state:
    if message.text == '\u2B05':
      await state.finish()
      await check_balance(message)


@dp.callback_query_handler(lambda c: c.data in ["bitcoin"], state=[Form.in_buy_tokens, Form.in_check_balance_buy_tokens])
async def process_callback(callback_query: CallbackQuery, state: FSMContext):
  current_state = await state.get_state()
  if current_state == Form.in_check_balance_buy_tokens.state or current_state == Form.in_buy_tokens.state:
    data = callback_query.data
    if data == 'bitcoin':
      await bot.send_message(callback_query.from_user.id, text=
  """Choose one of the payment plans. The US dollar value you choose will be converted in corresponding amount of BTC in the next message.
  
  💰 Pricing
  $2 - 20 000 tokens
  $5 - 100 000 tokens
  $10 - 300 000 tokens
  $20 - 800 000 tokens
  $40 - 2 000 000 tokens""", reply_markup=payment_plans_kb)

  
@dp.callback_query_handler(lambda c: c.data in ["2", "5", "10", "20", "40"], state=[Form.in_buy_tokens, Form.in_check_balance_buy_tokens])
async def pay_process(callback_query: CallbackQuery, state: FSMContext):
  current_state = await state.get_state()
  if current_state == Form.in_check_balance_buy_tokens.state or current_state == Form.in_buy_tokens.state:
    usd_value = callback_query.data
    if usd_value == '2':
      get_bitcoin_price = cg.get_price(ids='bitcoin', vs_currencies='usd')
      address = 'bc1qfghcxkz8hra9cq2k33rruuvqxc3kxft36afjuh'
      usd_value = int(usd_value)
      btc_price = get_bitcoin_price['bitcoin']['usd']
      qr = generate_qr(address, usd_value, btc_price)
      await bot.send_photo(chat_id=callback_query.message.chat.id, photo=qr, caption="Please scan this QR code to complete your payment")


@dp.message_handler(Text(equals='💼\nCheck balance'))
async def check_balance(message: Message):
  await Form.in_check_balance.set()
  user_id = message.from_user.id
  token_balance = get_token_balance(user_id)
  await bot.send_message(message.from_user.id, f'Your tokens: {token_balance}', reply_markup=check_balance_kb)


@dp.message_handler(state=Form.in_check_balance)
async def process_in_check_balance(message: Message, state: FSMContext):
  if message.text == '💳\nBuy tokens':
    await buy_tokens(message, state)
  elif message.text == '\u2B05':
    await state.finish()
    await bot.send_message(message.from_user.id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
    