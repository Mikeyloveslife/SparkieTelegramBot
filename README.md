# About Sparkie

Introducing the ultimate language model experience on Telegram - my latest project brings GPT language models to the messaging platform in a comprehensive and user-friendly way. With support for cutting-edge models, the Telegram bot gives users complete control over the settings that matter most - including temperature and maximum length - all directly from the bot interface.

Currently supported models:
- text-davinci-003;
- gpt-3.5-turbo.

All custom settings of your users being saved to sqlite3 database and fetched every time they perform an action in the bot.

Currently supported languages:
**- English;**
- Ukrainian;
- Russian.

# How to get started ?
1. First of all create your own telegram bot, save its api key as an environment variable.
2. Open create_bot.py file and replace "telegramBot_api" with the name of your environment variable instance.
3. To interact with the models we need openai api key, go and get it on https://platform.openai.com/ and save as environment variable too.
4. Then open each file in handlers folder and replace "OPENAI_API_KEY" with your the name of your environment variable from step 3.
5. Run your code and use it.
