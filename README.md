# Sparky AI


## A fully functional example of Telegram bot which utilizes OpenAI models

This is a versatile chatbot powered by OpenAI's GPT models capable of both text and image generation. It has built-in chat memory support and is designed for easy integration. After installation you can do the following:

* Automatically list every new user in sqlite3 database by Telegram user ID
* Chat with text-davinci-003 and gpt-3.5-turbo models
* Swap text-davinci-003 and gpt-3.5-turbo models in "Model settings"
* Customize temperature and max length for text-davinci-003 and save the preferences to sqlite3
* Count and save token usage



All custom settings of your users being saved to sqlite3 database and fetched every time they perform an action in the bot.

Currently supported languages:
- **English;**
- **Ukrainian;**
- **Russian.**

# How to get started ?
1. First of all create your own telegram bot, save its api key as an environment variable.
2. Open create_bot.py file and replace "telegramBot_api" with the name of your environment variable instance.
3. To interact with the models we need openai api key, go and get it on https://platform.openai.com/ and save as environment variable too.
4. Then open each file in handlers folder and replace "OPENAI_API_KEY" with your the name of your environment 
   variable from step 3.
5. Run your code and use it.
