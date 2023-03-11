import sqlite3 


# Create the database and table if they don't exist
def create_database():
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, language TEXT CHECK (language IN ('ENG', 'UKR', 'RU')), tokens INTEGER, max_length INTEGER, temperature REAL CHECK (temperature >= 0 AND temperature <= 1), model TEXT CHECK (model IN ('text-davinci-003', 'gpt-3.5-turbo')))''')
    conn.commit()

### Check if the user's Telegram ID is already in the database ###
def check_user_exists(user_id: int):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''SELECT user_id FROM users WHERE user_id = ?''',(user_id,))
    return cursor.fetchone() is not None

                     ### Get user language ###
def get_user_lang(user_id):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

                   ### Update user's language ###
def update_user_lang(user_id: int, lang: str):
  valid_lang = ('ENG', 'UKR', 'RU')
  if lang not in valid_lang:
    raise ValueError(f'Invalid language choice. Must be one of: {valid_lang}')
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id))
    conn.commit()

      
### The function gets token balance for users ###
def get_token_balance(user_id: int):
    with sqlite3.connect('user_settings.db') as conn:
      cursor = conn.cursor()
      cursor.execute('SELECT tokens FROM users WHERE user_id = ?', (user_id,))
      token_balance = cursor.fetchone()[0]
      return token_balance

# Add or update the user's token balance
def default_user_settings(user_id: int, tokens: int, max_length: int, temperature: float, model: str):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users(user_id, tokens, max_length, temperature, model) VALUES(?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET tokens = ?, max_length = ?, temperature = ?, model = ?''', (user_id, tokens, max_length, temperature, model, tokens, max_length, temperature, model))
    conn.commit()

              ### Getting 3 user settings for prompts ###
def get_text_davinci_003_settings(user_id: int):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT tokens, max_length, temperature FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
      return tuple(result)
    else:
      return None


### Gets token limit for users ###
def get_max_length(user_id: int):
    with sqlite3.connect('user_settings.db') as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT max_length FROM users WHERE user_id = ?",(user_id,))
      result = cursor.fetchone()
      if result:
          return result[0]
      else:
          return None

                  ### Update Maximum length ###
def update_max_length(user_id: int, max_length: int):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET max_length = ? WHERE user_id = ?", (max_length, user_id))
    conn.commit()

         ### The function gets token balance for users ###
def get_temperature(user_id: int):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT temperature FROM users WHERE user_id = ?", (user_id,))
    temperature = cursor.fetchone()
    if temperature:
      return temperature[0]
    else:
      return None

def update_temperature(user_id: int, temperature: float):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET temperature = ? WHERE user_id = ?",(temperature, user_id))
    conn.commit()

      ### subtruct tokens used in a prompt ###
def subtract_tokens(user_id: int, num_tokens_used: int):
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET tokens = tokens - ? WHERE user_id = ?', (num_tokens_used, user_id))
    conn.commit()


def get_model(user_id: int):
    with sqlite3.connect('user_settings.db') as conn:
      cursor = conn.cursor()
      cursor.execute("SELECT model FROM users WHERE user_id = ?",(user_id,))
      result = cursor.fetchone()
      if result:
          return result[0]
      else:
          return None

def update_model(user_id: int, model: str):
  valid_model = ('gpt-3.5-turbo', 'text-davinci-003')
  if model not in valid_model:
    raise ValueError(f'Invalid model choice. Must be one of: {valid_model}')
  with sqlite3.connect('user_settings.db') as conn:
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET model = ? WHERE user_id = ?', (model, user_id))
    conn.commit()