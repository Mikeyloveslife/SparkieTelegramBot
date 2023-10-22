# Sparky AI


## A fully functional example of Telegram bot which utilizes OpenAI models

This is a versatile chatbot powered by OpenAI's GPT models capable of both text and image generation. It has built-in chat memory support and is designed for easy integration. After installation you can do the following:

* Automatically list every new user in SQLite3 database by Telegram user ID as a primary key
* Automatically set default settings for every user(tokens, max_length, temperature, model)
* Chat with text-davinci-003 and gpt-3.5-turbo models
* Swap text-davinci-003 and gpt-3.5-turbo models in "Model settings"
* Customize temperature and max length for text-davinci-003 and save the preferences to SQLite3
* Count token usage for every text or image generation and save new balance in SQLite3 database

## Installation instructions
Here is a step-by-step tutorial on how to install Sparky on your machine.

1. Clone the repository in a directory of your preference.
```shell
git clone https://github.com/denyskarpov-eng/Sparkie-the-GPT-bot-for-Telegram.git
```
2. Create a virtual environment with python3-venv and install dependencies(you can also use poetry, conda or another method of your preference)
      * Install the Python module for virtual environments (venv) on your system.
          ```shell
          sudo apt install python3-venv
          ```
      * Navigate to the project directory using the cd command.
          ```shell
          cd pathtoprojectdirectory
          ```
      * Once you are in the desired directory, run the following command to create a new virtual environment:
          ```shell
          python3 -m venv myenv
          ```
          Replace myenv with the name you want to give to your virtual environment.
      * Activate the virtual environment by running the following command:
          ```shell
          source myenv/bin/activate
          ```
          Your terminal prompt should now show the name of the activated virtual environment.
      * Install necessary packages using pip:
          ```shell
          pip install aiogram==2.13 openai Pillow pycoingecko qrcode
          ```



4. Create environment variables in .env file: 
   * Open the cloned repository in your code editor
   * Add a new file called ".env"
   * Open .env file and insert your OpenAI API key and Telegram bot API.
```shell
OPENAI_API_KEY = replacewithyourOpenAIapikey
telegramBot_api = replacewithapitokenofyourTelegrambot
```


