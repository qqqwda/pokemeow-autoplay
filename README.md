# 🤖 PokeMeow autoplay

Python application designed to automate the process of catching Pokemons in the popular Discord game, PokeMeow. Utilizing the power of Selenium and ChromeDriver.
- I'll be updating this repo, in the future I will add an endpoint for Captcha Solving 🧩

## ⚠️ Disclaimer
Please note, while this bot is designed to automate tasks within PokeMeow, users are encouraged to use it responsibly and in accordance with the game's terms of service. The developer of this bot assumes no responsibility for any bans or penalties that may result from the use of this bot. Users should be aware of PokeMeow's rules and use the bot at their own risk.

## 📋 Requirements
- **Python 3.10:** This bot is developed and tested with Python 3.10. It is recommended to use this version for compatibility purposes, although other versions have not been tested. 🐍
- **Selenium 4.9.0:** For automating web browser interaction. 🌐
- **Requests:** For making HTTP requests. 📡
- **python-dotenv:** For managing environment variables. 🔑

## 🚀 Setup Instructions

1. **Install Python 3.10:** Ensure you have Python 3.10 installed on your system. You can download it from the official Python website. 📥
2. **Clone the Repository:** Clone this repository to your local machine or download the source code. 📂
3. **Check Chrome Version:** Before installing ChromeDriver, it's important to check your current version of Google Chrome to ensure compatibility. Open Google Chrome, click on the three dots in the upper right corner to open the menu, then go to "Help" > "About Google Chrome". Your Chrome version will be displayed here.
4. **Download Chrome Web Driver:** If you are using a Chrome version > 121 you can use this link: https://googlechromelabs.github.io/chrome-for-testing/ if not, use https://chromedriver.chromium.org/downloads and download the version that you need
5. **Install Dependencies:** Run `pip install -r requirements.txt` in your terminal to install the necessary dependencies. 🛠️
6. **Configure Environment Variables:** Create a `.env` file in the root directory and add your Discord and PokeMeow credentials. 📝
   ## ⚙️ Configuring Environment Variables

  Before running the PokeMeow Catcher Bot, you need to set up your environment variables. These variables include your Discord login credentials, the channel URL for catching Pokemons, the dictionary for Pokemon catching strategy, the path to your ChromeDriver, and the URL for the captcha prediction service.
  
  Create a `.env` file in the root directory of your project and populate it with the following variables:
  
  ```plaintext
  # Discord credentials
  DISCORD_EMAIL=yourloginemail@gmail.com
  PASSWORD=yourpassword
  
  # Channel URL
  CHANNEL=https://discord.com/channels/yourserverid/yourchannelid
  
  # Pokemon catching strategy dictionary
  POKEMON_DICTIONARY={"Legendary": "masterball", "Shiny": "masterball", "Super": "ultraball", "Rare": "greatball", "Uncommon": "pokeball", "Common": "pokeball"}
  
  # Path to your ChromeDriver
  DRIVER_PATH=path/to/your/chromedriver.exe
8. **Run the Bot:** Execute the bot script with Python to start catching Pokemons automatically. 🎮
   ```plaintext
    py main.py
    # Or
    python main.py

