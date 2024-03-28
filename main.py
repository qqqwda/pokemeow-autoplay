from logger import Logger
from driver import Driver
from dotenv import load_dotenv
load_dotenv()
import os
import time

DISCORD_EMAIL = os.getenv('DISCORD_EMAIL')
PASSWORD = os.getenv('PASSWORD')
CHANNEL = os.getenv('CHANNEL')
DRIVER_PATH = os.getenv('DRIVER_PATH')
logger = Logger.getInstance().get_logger()

if __name__ == "__main__":
    # Start the bot
    
    main = Driver(DRIVER_PATH)
    logger.info("🚀 Starting bot!")

    main.start_driver()
    main.navigate_to_page("https://discord.com/login")
    main.login(DISCORD_EMAIL,PASSWORD)
    main.navigate_to_page(CHANNEL)
    time.sleep(5)
    main.play()
    