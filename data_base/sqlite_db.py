import sqlite3 
from sqlite3 import Connection, Error
from aiogram.dispatcher.filters.state import State, StatesGroup

class All_states(StatesGroup):
  # states in english
  in_gpt_turbo_eng = State()
  in_text_davinci_003_eng = State()
  in_model_settings_eng = State()
  in_choose_model_eng = State()
  in_max_length_eng = State()
  in_temperature_eng = State()
  in_choose_lang_eng = State()
  # image generation states
  in_image_size = State()
  in_generate_image = State()
  in_generate_image_variation = State()
  # payments
  in_buy_tokens = State()
  in_check_balance = State()
  in_check_balance_buy_tokens = State()
  # states in russian
  in_gpt_turbo_ru = State()
  in_text_davinci_003_ru = State()
  in_model_settings_ru = State()
  in_choose_model_ru = State()
  in_max_length_ru = State()
  in_temperature_ru = State()
  in_choose_lang_ru = State()

class Database:
  def __init__(self, db_path):
    self.db_path = db_path
    self.conn_pool = []

  def get_connection(self) -> Connection:
    if self.conn_pool:
      return self.conn_pool.pop()
    else:
        try:
          return sqlite3.connect(self.db_path)
        except Error as e:
          print(e)
          return None

  def release_connection(self, conn: Connection):
    self.conn_pool.append(conn)

  ### CREATE DATABASE AND TABLE IF THEY DON'T EXIST ###
  def create_database():
    with sqlite3.connect('user_settings.db') as conn:
      cursor = conn.cursor()
      cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, language TEXT CHECK (language IN ('ENG', 'UKR', 'RU')), tokens INTEGER, max_length INTEGER, temperature REAL CHECK (temperature >= 0 AND temperature <= 1), model TEXT CHECK (model IN ('text-davinci-003', 'gpt-3.5-turbo')), chat_history TEXT, img_size TEXT CHECK (img_size IN ('256x256', '512x512', '1024x1024')))''')
      conn.commit()


  ### SET DEFAULT USER SETTINGS ###
  def set_default_user_settings(self, user_id: int, tokens: int, max_length: int, temperature: float, model: str, language: str):
    conn = self.get_connection()
    if conn is None:
      return
    try:
      cursor = conn.cursor()
      cursor.execute('''INSERT INTO users(user_id, tokens, max_length, temperature, model, language) VALUES(?, ?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET tokens = excluded.tokens, max_length = excluded.max_length, temperature = excluded.temperature, model = excluded.model, language = excluded.language''', (user_id, tokens, max_length, temperature, model, language))
      conn.commit()
    finally:
      self.release_connection(conn)

      
    
  ### UPDATE IMAGE_SIZE ###
  def update_img_size(self, user_id: int, img_size: str):
    valid_size = ('256x256', '512x512', '1024x1024')
    if img_size not in valid_size:
      raise ValueError(f'Invalid size choice. Must be one of: {valid_size}')
    conn = self.get_connection()
    if conn is None:
      return
    try:
      cursor = conn.cursor()
      cursor.execute('UPDATE users SET img_size = ? WHERE user_id = ?', (img_size, user_id))
      conn.commit()
    finally:
      self.release_connection(conn)

  ### GET IMG SIZE ###
  def get_img_size(self, user_id: int):
    conn = self.get_connection()
    if conn is None:
      return None
    try:
      cursor = conn.cursor()
      cursor.execute('SELECT img_size FROM users WHERE user_id = ?', (user_id,))
      result = cursor.fetchone()
      vals = {'256x256': 5336, '512x512': 6003, '1024x1024': 6670}
      if result:
        return result[0], vals[result[0]]
      else:
        return None
    finally:
        self.release_connection(conn) 


  ### SUBTRACT TOKENS USED IN A PROMPT ###
  def subtract_tokens(self, user_id: int, num_tokens_used: int):
    conn = self.get_connection()
    if conn is None:
      return
    try:
      cursor = conn.cursor()
      cursor.execute('UPDATE users SET tokens = tokens - ? WHERE user_id = ?', (num_tokens_used, user_id))
      conn.commit()
    finally:
      self.release_connection(conn)


  ### GET USER PARAM ###
  def get_param(self, user_id: int, param: tuple):
    conn = self.get_connection()
    if conn is None:
      return None
    try:
      cursor = conn.cursor()
      if len(param) > 1:
        param_string = ', '.join(param)
        cursor.execute(f"SELECT {param_string} FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
          return result
        else:
          return None
      else:
        cursor.execute(f"SELECT {param[0]} FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
          return result[0]
        else:
          return None
    finally:
      self.release_connection(conn)



  ### UPDATE USER PARAM ###
  def update_param(self, user_id: int, param: tuple):
    conn = self.get_connection()
    if conn is None:
      return None
    try:
      cursor = conn.cursor()
      cursor.execute(f"UPDATE users SET {param[0]} = ? WHERE user_id = ?", (param[1], user_id))
    finally:
      self.release_connection(conn)


      


