# 🤖 PokeMeow autoplay

Python application designed to automate the process of catching Pokemons in the popular Discord game, PokeMeow. Utilizing the power of Selenium and ChromeDriver.
- I'll be updating this repo, in the future I will add an endpoint for Captcha Solving 🧩
- New API for captcha solver: https://rapidapi.com/qqqwda/api/pokemeow-captcha-solver (Note: this might work slow)
  ```plaintext
  import requests
      
  url = "https://pokemeow-captcha-solver.p.rapidapi.com/predict"
      
  files = { "file": "open('captcha-file.png', 'rb')" }
  headers = {
  "X-RapidAPI-Key": "3fe858485cmsh4b09dad8226ecc6p149f14jsn799ac3bc7fb1",
  "X-RapidAPI-Host": "pokemeow-captcha-solver.p.rapidapi.com"
  }
      
  response = requests.post(url, files=files, headers=headers)
  print(response.json())
    ```

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
3. **Check Chrome Version:** Before installing ChromeDriver, it's important to check your current version of Google Chrome to ensure compatibility. Open Google Chrome, click on the three dots in the upper right corner to open the menu, then go to "Help" > "About Google Chrome". Your Chrome version will be displayed here. 🔍
4. **Download ChromeDriver:** Depending on your Chrome version, download the corresponding ChromeDriver.
   - For Chrome Version 121 or higher: [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
   - For Chrome Version lower than 121: [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Paste / Replace the `chromedriver.exe` inside the `'webdrivers\Chrome'` folder. 📦
5. **Install Dependencies:** Run `pip install -r requirements.txt` in your terminal to install the necessary dependencies. 🛠️
6. **Configure Environment Variables:** Setup your environment variables by creating a `.env` file in the root directory. Include your Discord and PokeMeow credentials, channel URL, Pokemon catching strategy dictionary, ChromeDriver path, and the URL for the captcha prediction service. ⚙️

    Create or use my `.env` file with the following structure:

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
    ```

    Replace the placeholders with your actual data.

7. **Run the Bot:** Execute the bot script with Python to start catching Pokemons automatically. Use the following command to run your bot: 🎮

    ```bash
    python main.py
    ```

Ensure you replace placeholder values with your actual data before proceeding. This setup guide is designed to help you get started with the PokeMeow Catcher Bot quickly and efficiently.

## 📬 Contact

For support, questions, or collaboration, feel free to contact me on Discord:

- Discord: cursedelboom
