from create_bot import dp, bot
from aiogram.types import Message, CallbackQuery
#from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_base.sqlite_db import Database
from keyboards.keyboards_eng import menu_kb, check_balance_kb, payment_plans_kb, bitcoin_kb, return_kb

from data_base.sqlite_db import All_states
db = Database('user_settings.db')

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

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


@dp.message_handler(text='💳\nBuy tokens')
async def buy_tokens(message: Message, state: FSMContext):
  current_state = await state.get_state()
  user_id = message.from_user.id
  token_balance = db.get_param(user_id, ("tokens",))
  if current_state == All_states.in_check_balance.state:
    await All_states.in_buy_tokens.set()
    await bot.send_message(user_id,'Choose one of our payment providers:', reply_markup=bitcoin_kb)
    await bot.send_message(user_id, f'Your token balance is {token_balance}.', reply_markup=return_kb)
    await All_states.in_check_balance_buy_tokens.set()
  else:
    await All_states.in_buy_tokens.set()
    await bot.send_message(user_id,'Choose one of our payment providers:', reply_markup=bitcoin_kb)
    await bot.send_message(user_id, f'Your token balance is {token_balance}.', reply_markup=return_kb)

@dp.message_handler(state=[All_states.in_buy_tokens, All_states.in_check_balance_buy_tokens])
async def in_buy_tokens(message: Message, state: FSMContext):
  current_state = await state.get_state()
  if current_state == All_states.in_buy_tokens.state:
    if message.text == '⬅️':
      await state.finish()
      await bot.send_message(message.from_user.id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
  elif current_state == All_states.in_check_balance_buy_tokens.state:
    if message.text == '⬅️':
      await state.finish()
      await check_balance(message)


@dp.callback_query_handler(lambda c: c.data in ["bitcoin"], state=[All_states.in_buy_tokens, All_states.in_check_balance_buy_tokens])
async def process_callback(callback_query: CallbackQuery, state: FSMContext):
  current_state = await state.get_state()
  if current_state == All_states.in_check_balance_buy_tokens.state or current_state == All_states.in_buy_tokens.state:
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

  
@dp.callback_query_handler(lambda c: c.data in ["2", "5", "10", "20", "40"], state=[All_states.in_buy_tokens, All_states.in_check_balance_buy_tokens])
async def pay_process(callback_query: CallbackQuery, state: FSMContext):
  current_state = await state.get_state()
  if current_state == All_states.in_check_balance_buy_tokens.state or current_state == All_states.in_buy_tokens.state:
    usd_value = callback_query.data
    if usd_value == '2':
      get_bitcoin_price = cg.get_price(ids='bitcoin', vs_currencies='usd')
      address = 'bc1qfghcxkz8hra9cq2k33rruuvqxc3kxft36afjuh'
      usd_value = int(usd_value)
      btc_price = get_bitcoin_price['bitcoin']['usd']
      qr = generate_qr(address, usd_value, btc_price)
      await bot.send_photo(chat_id=callback_query.message.chat.id, photo=qr, caption="Please scan this QR code to complete your payment")


@dp.message_handler(text="💼\nCheck balance")
async def check_balance(message: Message):
  await All_states.in_check_balance.set()
  user_id = message.from_user.id
  token_balance = db.get_param(user_id, ("tokens",))
  await bot.send_message(user_id, f"Your token balance: {token_balance}", reply_markup=check_balance_kb)



#@dp.message_handler(state=All_states.in_check_balance)
async def process_in_check_balance(message: Message, state: FSMContext):
  user_id = message.from_user.id
  print("IN CHECK BALANCE STATE MA MAN")
  if message.text == '💳\nBuy tokens':
    await buy_tokens(message, state)
  elif message.text == '⬅️':
    await state.finish()
    await bot.send_message(user_id, "Welcome to the main menu. Please select an option:", reply_markup=menu_kb)
    