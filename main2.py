from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import uuid
from selenium.webdriver.common.by import By
import requests
from dotenv import load_dotenv
import json
import logging
from bs4 import BeautifulSoup
import re
import threading
import warnings
import random
from buy import Buy
from inventory import Inventory
from counter import save_catch_counter, load_catch_counter

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Your code here
load_dotenv()
# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DISCORD_EMAIL = os.getenv('DISCORD_EMAIL')
PASSWORD = os.getenv('PASSWORD')
CHANNEL = os.getenv('CHANNEL')
POKEMON_DICTIONARY = json.loads(os.getenv('POKEMON_DICTIONARY'))
RARITY_EMOJI = json.loads(os.getenv('RARITY_EMOJI'))
PREDICT_CAPTCHA_URL = os.getenv('PREDICT_CAPTCHA_URL')
DRIVER_PATH = os.getenv('DRIVER_PATH')
API_KEY = os.getenv('API_KEY')

# Create handlers
c_handler = logging.StreamHandler()
# Create a file handler
f_handler = logging.FileHandler('file.log', encoding='utf-8')

c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.ERROR)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

class Main:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

    def start_driver(self):
        # Set up Chrome options
        options = Options()
        options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(executable_path=self.driver_path, options=options)

    def navigate_to_page(self, url):
        if self.driver is not None:
            self.driver.get(url)
        else:
            logger.info("Driver not started. Call start_driver first.")

    def quit_driver(self):
        if self.driver is not None:
            self.driver.quit()
        else:
            logger.info("Driver not started. Nothing to quit.")
            
    def login(self, email, password):
        time.sleep(5)
        self.driver.find_element(
            "xpath", "//input[@class='inputDefault__80165 input_d266e7 inputField__79601']").send_keys(email)
        self.driver.find_element(
            "xpath", "//input[@class='inputDefault__80165 input_d266e7']").send_keys(password)
        time.sleep(3)
        self.driver.find_element(
            "xpath", "//button[@class='marginBottom8_f4aae3 button__47891 button_afdfd9 lookFilled__19298 colorBrand_b2253e sizeLarge__9049d fullWidth__7c3e8 grow__4c8a4']").click()

        time.sleep(8)
        pass
    
    def get_last_message_by_user(self, username):
        try:
            # Fetch all message elements
            messages = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'messageListItem__6a4fb')]")

            # Iterate over messages in reverse to find the last message from the user
            for message in reversed(messages):
                user_elements = message.find_elements(By.XPATH, ".//span[contains(@class, 'username_d30d99')]")
                if user_elements:
                    user_element = user_elements[-1]
                    if username in user_element.text:
                        # Find the message content
                        message_content = message.find_elements(By.XPATH, ".//div[contains(@class, 'messageContent__21e69')]")[-1]
                        return message_content.text

            return "Message from user not found."

        except NoSuchElementException:
            return "Error: Unable to locate element."
           
    def get_last_element_by_user(self, username):
        try:
            # Fetch all message elements
            messages = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'messageListItem__6a4fb')]")

            # Iterate over messages in reverse to find the last message from the user
            for message in reversed(messages):
                user_elements = message.find_elements(By.XPATH, ".//span[contains(@class, 'username_d30d99')]")
                if user_elements:
                    user_element = user_elements[-1]
                    if username in user_element.text:
                        # Find the message content
                        return message

            return "Message from user not found."

        except NoSuchElementException:
            return "Error: Unable to locate element."
    
    def get_captcha(self):
        # Find the div element by its classes
        # div_element = self.driver.find_element_by_css_selector(".imageContent__24964.embedWrapper_c143d9.embedMedia_b473d2.embedImage_e638a7")
        div_element = self.get_last_element_by_user("PokéMeow")
        
        # Find the first a element within the div element
        a_element = div_element.find_elements(By.TAG_NAME, "a")[-1]

        # Now you can get the href attribute or do whatever you need with the a element
        href = a_element.get_attribute("href")
        img_path = self.download_captcha(href)
        
        return self.send_image(img_path)
        
    def download_captcha(self, href):
        image_url = href

        # Create the directory if it doesn't exist
        if not os.path.exists("captchas"):
            os.makedirs("captchas")

        # Generate a unique ID for the image
        image_id = uuid.uuid4()

        # Send a HTTP request to the URL of the image
        response = requests.get(image_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Open the file in write mode, write the contents of the response to it, and close it
            with open(f"captchas/image_{image_id}.png", "wb") as file:
                file.write(response.content)
                # Get the list of files in the captchas directory
            files = os.listdir("captchas")
            # Print the number of files with an emoji
            logger.info(f'📂 Number of images in captcha folder: {len(files)}')
            
            
            return f"captchas/image_{image_id}.png"
        
        return None
    
    def send_image(self, image_path):
        url = PREDICT_CAPTCHA_URL
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "pokemeow-captcha-solver.p.rapidapi.com"
        }

        # Open the image file in binary mode
        with open(image_path, "rb") as image_file:
            # Create a dictionary with the file
            files = {"file": image_file}

            for _ in range(3):  # Retry up to 3 times
                logger.info("🚀 Sending image to RapidApi...")

                try:
                    # Make the POST request and get the response
                    response = requests.post(url, files=files, headers=headers, timeout=10)  # Wait up to 10 seconds

                    # If the request was successful, print the number from the response
                    if response.status_code == 200:
                        logger.info("✅ Image sent successfully!")
                        return response.json()["number"]
                    else:
                        logger.info("❌ Failed to send image")
                        # logger.info(f"❌ Message: {response.json()['messages']}")
                except requests.exceptions.Timeout:
                    logger.info("⏰ Request timed out, retrying...")

                # Wait for a bit before retrying
                time.sleep(5)

        logger.info("❌ Failed to send image after 3 attempts")
    
    def solve_captcha(self):
        resp = self.get_captcha()
        logger.info(f'🔒 captcha response: {resp}')
        self.write(resp)
        time.sleep(4)
                
        pokemeow_last_message = self.get_last_message_by_user("PokéMeow")
        if "Thank you" in pokemeow_last_message:
            logger.info('🔓 Captcha solved!')
            return
        else:
            logger.info('❌ Captcha failed!')
            logger.info('❌ Trying again!')
            self.solve_captcha()
    
    def write(self, msg):
        span = self.driver.find_element("xpath", "//span[@class='emptyText_c03d90']")
        ActionChains(self.driver).send_keys_to_element(span, Keys.BACK_SPACE*20).send_keys_to_element(span, msg).perform()
        ActionChains(self.driver).send_keys_to_element(span, Keys.ENTER).perform()
 
    def wait_for_solve_captcha(self):
        # resp = self.get_captcha()
        logger.info(f'🔒 Waiting for you to solve captcha... ')
        time.sleep(4)
                
        pokemeow_last_message = self.get_last_message_by_user("PokéMeow")
        if "Thank you" in pokemeow_last_message:
            logger.info('🔓 Captcha solved!')
            return
        else:
            self.wait_for_solve_captcha()
    
    def get_next_ball(self, current_ball):
        balls_priority = {
            "masterball": 4,
            "ultraball": 3,
            "greatball": 2,
            "pokeball": 1
        }

        # Get the priority of the current ball
        current_priority = balls_priority.get(current_ball)

        # If the current ball is not in the dictionary or it's a Pokeball, return None
        if current_priority is None or current_priority == 1:
            return None

        # Find the ball with the next highest priority
        for ball, priority in sorted(balls_priority.items(), key=lambda item: item[1], reverse=True):
            if priority < current_priority:
                return ball
    
    def click_on_ball(self, ball):
        # Attempt to find the specific ball first.
        try:
            last_element_html = self.get_last_element_by_user("PokéMeow")

            balls = last_element_html.find_elements("css selector",f'img[alt="{ball}"]')
            # balls = last_element_html.find_elements_by_css_selector(f'img[alt="{ball}"]')
            if balls:
                # If the specific ball is found, click on the last occurrence of that ball.
                balls[-1].click()
            else:
                next_ball = self.get_next_ball(ball)
                logger.info(f"❌ {ball} not found. Trying {next_ball}")
                self.click_on_ball(next_ball)
                
        except Exception as e:
            logger.log(f"An error occurred: {e}")
       
    def get_catch_result(self, pokemon_info, count):
        if isinstance(pokemon_info, str):
            pokemon_info = json.loads(pokemon_info)
        # Find all elements containing the ✅ emoji
        time.sleep(3)
        last_element_html = self.get_last_element_by_user("PokéMeow")
        soup = BeautifulSoup(last_element_html.get_attribute('outerHTML'), "html.parser")
        emoji_elements = soup.find_all(string=lambda text: '✅' in text)

        # Get the Pokemon name and rarity from pokemon_info
        pokemon_name = pokemon_info.get('Name')
        pokemon_rarity = pokemon_info.get('Rarity')
        emoji = RARITY_EMOJI.get(pokemon_rarity, '')
        # Check if any element contains the ✅ emoji
        if emoji_elements:
            span = soup.find('span', {'class': 'embedFooterText_dc937f'})

            # Get the text of the span
            text = span.get_text()

            # Use a regular expression to find the earned coins
            earned_coins = re.search(r'earned ([\d,]+) PokeCoins', text)
            earned_coins = int(earned_coins.group(1).replace(',', ''))

            # Print the Pokemon name, rarity, and earned coins in one line
            logger.info(f'[{count}]✅ Pokemon Name: {pokemon_name}, Rarity: {pokemon_rarity} {emoji}, Earned Coins: {earned_coins} 💰')
                
        else:
            logger.info(f'[{count}]❌ Pokemon Name: {pokemon_name}, Rarity: {pokemon_rarity} {emoji}')
     
    def get_inventory(self):
        time.sleep(1)
        self.write(";inv")
        # Wait to load inventory
        time.sleep(3.5)
        last_element_html = self.get_last_element_by_user("PokéMeow")
        
        inventory_json = Inventory.get_inventory(last_element_html)
        if not inventory_json:
            logger.info("❌Failed to get inventory.")
            return
        
        # Load JSON into a Python object
        inventory = json.loads(inventory_json)

        return inventory
        
    def open_lootbox(self, inventory):
        for item in inventory:
            # Check if the item name is pokecoin
            if item["name"] == "lootbox":
                # Update pokecoin count
                lootboxes = item["count"]
                if lootboxes > 0:
                    time.sleep(3)
                    self.write(";lb all")
                break
    
    def buy_balls(self, inventory):
        # Initialize pokecoin count to 0
        budget = 0

        # Iterate over the inventory list
        for item in inventory:
            # Check if the item name is pokecoin
            if item["name"] == "pokecoin":
                # Update pokecoin count
                budget = item["count"]
                if budget > 200000:
                    budget = 200000
                break
            
        commands = Buy.generate_purchase_commands(budget)
        if not commands:
            logger.info("❌Not Enought budget to buy balls.")
            return
        
        for command in commands:
            #Wait 3 scs before writing next command
            logger.info(f'💰 {command}')
            self.write(command)
            time.sleep(5.5)
                       
    def get_pokemon_info(self):
        
        pokemon_info = {}
        # Assuming self.get_last_element_by_user("PokéMeow") returns the HTML content of the last element by the user "PokéMeow"
        last_element_html = self.get_last_element_by_user("PokéMeow")

        # Parse the HTML content
        soup = BeautifulSoup(last_element_html.get_attribute('outerHTML'), "html.parser")
        # Find the element containing the Pokémon description
        pokemon_description = soup.find("div", class_="embedDescription__33443")

        if pokemon_description:
            # Find all strong elements within the description
            strong_elements = pokemon_description.find_all("strong")

            if strong_elements:
                # Get the last strong element
                last_strong_element = strong_elements[-1]

                # Extract Pokémon name
                pokemon_info["Name"] = last_strong_element.get_text(strip=True)
                
        span = soup.find('span', {'class': 'embedFooterText_dc937f'}) 
        text = span.get_text()
        # Use a regular expression to find the rarity
        rarity = re.search(r'(.+?)\s*\(', span.get_text())

        # Check if a match was found
        if rarity:
            # Get the first group of the match
            rarity = rarity.group(1).strip()
            pokemon_info["Rarity"] = rarity

        # Use a regular expression to find all occurrences of 'word: number'
        matches = re.findall(r'(\w+)\s*:\s*([\d,]+)', text)

        # Convert the matches to a dictionary
        data = {k: int(v.replace(',', '')) for k, v in matches}
        pokemon_info["Balls"] = data
        
        # Convert the dictionary to a JSON string
        json_data = json.dumps(pokemon_info)

        # Convert dictionary to JSON
        pokemon_json = json.dumps(pokemon_info, indent=4)
        return pokemon_json
            
    def play(self):
        #Waits 4 seconds for the page to load 
        catch_counter = load_catch_counter()
        time.sleep(3)
        self.write(";daily")
        time.sleep(4)
        self.write(";quest")
        time.sleep(4)
        while True:
            sleep_time = random.randint(9, 12)  # Random integer between 1 and 5
            self.write(";p")
            #Wait for message from pokemeow
            time.sleep(3)   
            pokemeow_last_message = self.get_last_message_by_user("PokéMeow")
            
            if "Please wait" in pokemeow_last_message:
                #Go back to the start of the loop
                time.sleep(1)
                continue
            
            if "TYPE" in pokemeow_last_message.lower():
                logger.info('🔒 Captcha detected!')
                self.solve_captcha()
                continue
                    
            texto = self.driver.find_elements(
                "xpath", "//span[@class='embedFooterText_dc937f']")[-1].text
            
            arraytext = texto.split()
            
            rarity = arraytext[0]

            ball = POKEMON_DICTIONARY.get(rarity)

            if ball == None:
                self.solve_captcha()
                sleep_time = 1
                
            else:
                self.click_on_ball(ball)
                
                pokemon_info_json = self.get_pokemon_info()
                info = json.loads(pokemon_info_json)
                catch_counter += 1
                save_catch_counter(catch_counter)
                threading.Thread(target=self.get_catch_result, args=(pokemon_info_json,catch_counter,)).start()
                
                # Now you can access the elements of pokemon_info as a dictionary
                
                if info["Balls"]["Pokeballs"] <= 1 or info["Balls"]["Greatballs"] <= 1:
                    inventory = self.get_inventory()
                    self.buy_balls(inventory)
                
                if catch_counter % 25 == 0:
                    self.write(";r d")
                    time.sleep(4)
                    inventory = self.get_inventory()
                    self.open_lootbox(inventory)
                
                if catch_counter % 100 == 0:
                    self.write(";quest")
            # Save current catch count in memory
            
            time.sleep(sleep_time)



if __name__ == "__main__":
    logger.info('🚀 Starting bot!')
    main = Main(DRIVER_PATH)
    main.start_driver()
    main.navigate_to_page("https://discord.com/login")
    main.login(DISCORD_EMAIL,PASSWORD)
    main.navigate_to_page(CHANNEL)
    main.play()
    
    

    
