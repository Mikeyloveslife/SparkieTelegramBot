from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton


b1 = KeyboardButton(text='💬 Chat with Sparkie')
b2 = KeyboardButton(text='Create content')
b3 = KeyboardButton(text='🖼️ Image generation')
buy_tokens = KeyboardButton(text='💳\nBuy tokens')
b5 = KeyboardButton(text='💼\nCheck balance')
lang = KeyboardButton(text='🌐', callback_data="\U0001F310")

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

menu_kb.row(b1, b3)
menu_kb.row(buy_tokens, b5, lang)


                    ### Go back button and ? button ###

return_button = KeyboardButton(text='\u2B05')
question_button = KeyboardButton(text='\uFF1F')

return_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
return_kb.row(return_button, question_button)

                  ### in_text_davinci_003 keyboard ###
model_settings = KeyboardButton(text='⚙️\nModel settings')
choose_model = KeyboardButton(text='🕹\nChoose model')

in_text_davinci_003_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
in_text_davinci_003_kb.row(return_button, model_settings, choose_model)

                      ### in_gpt_turbo keyboard ###
in_gpt_turbo_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
in_gpt_turbo_kb.row(return_button, choose_model)

                  ### Prompt settings keyboard ###
max_length = KeyboardButton(text='Maximum length')
temperature = KeyboardButton(text='Temperature')
model_settings_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
model_settings_kb.row(return_button, max_length, temperature)

                 ### Temperature keyboard ###
max_length_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
max_length_kb.row(return_button, question_button)

                 ### Temperature inline keyboard ###
t0 = InlineKeyboardButton(text='0', callback_data="0")
t01 = InlineKeyboardButton(text='0.1', callback_data="0.1")
t02 = InlineKeyboardButton(text='0.2', callback_data="0.2")
t03 = InlineKeyboardButton(text='0.3', callback_data="0.3")
t04 = InlineKeyboardButton(text='0.4', callback_data="0.4")
t05 = InlineKeyboardButton(text='0.5', callback_data="0.5")
t06 = InlineKeyboardButton(text='0.6', callback_data="0.6")
t07 = InlineKeyboardButton(text='0.7', callback_data="0.7")
t08 = InlineKeyboardButton(text='0.8', callback_data="0.8")
t09 = InlineKeyboardButton(text='0.9', callback_data="0.9")
t10 = InlineKeyboardButton(text='1.0', callback_data="1.0")

temperature_inlinekeyboard = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
temperature_inlinekeyboard.row(t0, t01).row(t02, t03).row(t04, t05).row(t06, t07).row(t08, t09).row(t10)

temperature_replykeyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
temperature_replykeyboard.row(return_button, question_button)


                  ###Check balance keyboard ###
check_balance_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
check_balance_kb.row(return_button ,buy_tokens)


          ### Inline keyboard for "Buy tokens" button ###
buy_tokens_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
buy_tokens_kb.row(return_button, question_button)

p1 = InlineKeyboardButton(text='Bitcoin', callback_data="bitcoin")
bitcoin_kb = InlineKeyboardMarkup(row_width=1)
bitcoin_kb.row(p1)

            ### Inline keyboard for Buy tokens/Bitcoin ###
p1 = InlineKeyboardButton(text='$2', callback_data="2")
p2 = InlineKeyboardButton(text='$5', callback_data="5")
p3 = InlineKeyboardButton(text='$10', callback_data="10")
p4 = InlineKeyboardButton(text='$20', callback_data="20")
p5 = InlineKeyboardButton(text='$40', callback_data="40")
payment_plans_kb = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
payment_plans_kb.row(p1, p2).row(p3, p4).row(p5)



                ### Choose language keyboard ###

l1 = InlineKeyboardButton(text='🇺🇸 English', callback_data="ENG")
l2 = InlineKeyboardButton(text='🇺🇦 Українська', callback_data="UKR")
l3 = InlineKeyboardButton(text='🇷🇺 Русский', callback_data="RU")
language_kb = InlineKeyboardMarkup(row_width=3)
language_kb.row(l1, l2, l3)


m1 = InlineKeyboardButton(text='🤖 gpt-3.5-turbo', callback_data="gpt-3.5-turbo")
m2 = InlineKeyboardButton(text='🤖 text-davinci-003', callback_data="text-davinci-003")
model_kb = InlineKeyboardMarkup(row_width=1)
model_kb.row(m1).row(m2)




         ### Inline keyboard for Create content button ### 

c1 = InlineKeyboardButton(text='Post', callback_data="post")
c2 = InlineKeyboardButton(text='Article', callback_data="article")
c3 = InlineKeyboardButton(text='Story', callback_data="story")
c4 = InlineKeyboardButton(text='Business letter', callback_data="business letter")
c5 = InlineKeyboardButton(text='Commercial', callback_data="commercial")
c6 = InlineKeyboardButton(text='Your content', callback_data="your content")

choose_content_type_kb = InlineKeyboardMarkup(row_width=2)
choose_content_type_kb.row(c1, c2).row(c3, c4).row(c5, c6)


                

                ### IMAGE GENERATION KEYBOARDS ###
i1 = InlineKeyboardButton(text='Create image', callback_data='create image')
i2 = InlineKeyboardButton(text='Create image variation', callback_data='create image variation')

image_generation_inline_kb = InlineKeyboardMarkup(row_width=2)
image_generation_inline_kb.row(i1, i2)


