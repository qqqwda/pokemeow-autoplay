from logger import Logger
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time
from captcha_service import CaptchaService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from counter import save_catch_counter, load_catch_counter
import random
import json
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv
import msvcrt
from inventory import Inventory
from buy import Buy
from selenium.common.exceptions import TimeoutException
import configparser

load_dotenv()
config = configparser.ConfigParser()
config.read('config.ini')
# Get the JSON string from the .ini file
pokeball_for_pokemon_string = config.get('settings', 'pokemon_pokeball_mapping')
# Parse the JSON string as a dictionary
pokeball_for_pokemon = json.loads(pokeball_for_pokemon_string)


POKEMON_DICTIONARY = json.loads(os.getenv('POKEMON_DICTIONARY'))
RARITY_EMOJI = json.loads(os.getenv('RARITY_EMOJI'))
logger = Logger.getInstance().get_logger()
captcha_service = CaptchaService()

ENABLE_AUTO_BUY_BALLS=os.getenv('ENABLE_AUTO_BUY_BALLS')
ENABLE_AUTO_RELEASE_DUPLICATES=os.getenv('ENABLE_AUTO_RELEASE_DUPLICATES')
ENABLE_AUTO_EGG_HATCH=os.getenv('ENABLE_AUTO_EGG_HATCH')
ENABLE_AUTO_LOOTBOX=os.getenv('ENABLE_AUTO_LOOTBOX_OPEN')

class Driver:
    def __init__(self, driver_path):
        # Instance logger
        load_dotenv()
        self.driver_path = driver_path
        self.driver = None
        
    def start_driver(self):
        # Set up Chrome options
        options = Options()
        options.add_argument("--log-level=3")
        #Open the browser 800x700
        options.add_argument("--window-size=800,700")
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
        
        self.driver.find_element(By.XPATH, "//input[@name='email']").send_keys(email)
        
        self.driver.find_element(By.XPATH, "//input[@name='password']").send_keys(password)
        time.sleep(3)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

        time.sleep(8)
        pass 


    def write(self, msg):
        # span = self.driver.find_element(By.XPATH, "//span[contains(@class='emptyText'])")
        span = self.driver.find_element(By.XPATH, "//span[contains(@class, 'emptyText')]")

        ActionChains(self.driver).send_keys_to_element(span, Keys.BACK_SPACE*20).send_keys_to_element(span, msg).perform()
        ActionChains(self.driver).send_keys_to_element(span, Keys.ENTER).perform()
    
    def get_last_message_from_user(self, username):
        try:
            # Fetch all message elements
            messages = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'messageListItem')]")

            # Iterate over messages in reverse to find the last message from the user
            for message in reversed(messages):
                user_elements = message.find_elements(By.XPATH, ".//span[contains(@class, 'username')]")
                if user_elements:
                    user_element = user_elements[-1]
                    if username in user_element.text:
                        # Find the message content
                        return message

            logger.info(f"Message from {username} not found.")
            return None

        except NoSuchElementException:
            logger.info("Error: Unable to locate element.")
            return None
        
    def get_captcha(self):
        try:
            div_element = self.get_last_message_from_user("PokéMeow")
            
            # Find the first a element within the div element
            a_element = div_element.find_elements(By.TAG_NAME, "a")[-1]

            # Now you can get the href attribute or do whatever you need with the a element
            href = a_element.get_attribute("href")
            
            img_path = captcha_service.download_captcha(href)
            
            return captcha_service.send_image(img_path)
        except StaleElementReferenceException:
            logger.error("StaleElementReferenceException occurred. Retrying...")
            time.sleep(1)
            return self.get_captcha()
    
    
    def get_last_element_by_user(self, username, timeout=30) -> WebElement:
        try:
            # Wait for a new message from the user to appear
            WebDriverWait(self.driver, timeout).until(
                lambda driver: self.check_for_new_message(username)
            )
            
            # Fetch all message elements
            messages = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'messageListItem')]")

            # Iterate over messages in reverse to find the last message from the user
            for message in reversed(messages):
                user_elements = message.find_elements(By.XPATH, ".//span[contains(@class, 'username')]")
                if user_elements:
                    user_element = user_elements[-1]
                    if username in user_element.text:
                        # Return the message element
                        return message

            logger.error(f"Message from {username} not found.")
            return None

        except TimeoutException:
            logger.error(f"Message from {username} not found. Timeout exceeded.")
            return None

        except NoSuchElementException:
            logger.error("Error: Unable to locate element.")
            return None

    def check_for_new_message(self, username):
        # Fetch all message elements
        messages = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'messageListItem')]")

        # Check if the last message is from the user
        if messages:
            try:
                last_message = messages[-1]
                user_elements = last_message.find_elements(By.XPATH, ".//span[contains(@class, 'username')]")
                for user_element in user_elements:
                    if username in user_element.text:
                        return True
                return False
            except StaleElementReferenceException:
                return False

        return False
    
    def wait_for_element_text_to_change(self, element, timeout=15) -> WebElement:
        try:
            # Store the initial text of the element
            initial_text = element.text

            # Wait for the text of the element to change
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # If the text of the element has changed, return the new text
                    if element.text != initial_text:
                        return element
                except StaleElementReferenceException:
                    # If the element is no longer attached to the DOM, return None
                    logger.error("Element is no longer attached to the DOM")
                    return None

                # Wait before checking the text of the element again
                time.sleep(1)

            # If the timeout is reached without the text of the element changing, return None
            logger.warning("Timeout reached without text change")
            return None

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    
    def solve_captcha(self, element):
        
        #Download the captcha image and send it to the API
        number = self.get_captcha()
        
        # Write the captcha number in the chat
        logger.info(f"🔢 Captcha response: {number}")
        self.write(number)
        
        # Waits 120 seconds for the captcha to be solved
        pokemeow_last_message = self.wait_for_element_text_to_change(element, timeout=120)
        
        if "Thank you" in pokemeow_last_message.text:
            logger.warning('Captcha solved, continuing...')
            return
        else:
            logger.error('Captcha failed, trying again!')
            new_captcha_element = self.get_last_message_from_user("PokéMeow")
            self.solve_captcha(new_captcha_element)
    
    
    def get_spawn_info(self, element):
        
        pokemon_info = {}
        
        # Parse the HTML content
        soup = BeautifulSoup(element.get_attribute('outerHTML'), "html.parser")
        # Find the element containing the Pokémon description
        pokemon_description = soup.select_one("div[class*='embedDescription']")

        pokemon_info["Item"] = data = soup.find('img', {'aria-label': ':held_item:'}) is not None

        if pokemon_description:
            # Find all strong elements within the description
            strong_elements = pokemon_description.find_all("strong")

            if strong_elements:
                # Get the last strong element
                last_strong_element = strong_elements[-1]

                # Extract Pokémon name
                pokemon_info["Name"] = last_strong_element.get_text(strip=True)
                
        # span = soup.find('span', {'class': 'embedFooterText_dc937f'}) 
        span = soup.select_one("span[class*='embedFooterText']")

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
    
    def get_next_ball(self, current_ball):
        balls_priority = {
            "masterball": 5,
            "premierball": 4,
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
            time.sleep(1)
            last_element_html = self.get_last_element_by_user("PokéMeow")
            balls = last_element_html.find_elements("css selector",f'img[alt="{ball}"]')
            if balls:
                # If the specific ball is found, click on the last occurrence of that ball.
                balls[-1].click()
            else:
                next_ball = self.get_next_ball(ball)
                logger.info(f"❌ {ball} not found. Trying {next_ball}")
                self.click_on_ball(next_ball)
                
        except Exception as e:
            logger.log(f"An error occurred: {e}")
    
    def get_inventory(self):
        time.sleep(1)
        self.write(";inv")
        # Wait to load inventory
        last_element_html = self.get_last_element_by_user("PokéMeow")
        
        inventory_json = Inventory.get_inventory(last_element_html)
        if not inventory_json:
            logger.info("❌Failed to get inventory.")
            return
        
        # Load JSON into a Python object
        inventory = json.loads(inventory_json)

        return inventory
    
    
    def get_catch_result(self, pokemon_info, count, element):
        if isinstance(pokemon_info, str):
            pokemon_info = json.loads(pokemon_info)

        soup = BeautifulSoup(element.get_attribute('outerHTML'), "html.parser")
        pokemon_was_catched = soup.find_all(string=lambda text: '✅' in text)

        # Get the Pokemon name and rarity from pokemon_info
        pokemon_name = pokemon_info.get('Name')
        pokemon_rarity = pokemon_info.get('Rarity')
        has_item = pokemon_info.get('Item')
        emoji = RARITY_EMOJI.get(pokemon_rarity, '')
        # Check if any element contains the ✅ emoji
        if pokemon_was_catched:
            
            span = soup.find('span', class_=lambda value: value and 'embedFooterText' in value)

            # Get the text of the span
            text = span.get_text()

            # Use a regular expression to find the earned coins
            earned_coins = re.search(r'earned ([\d,]+) PokeCoins', text)
            
            # Assuming earned_coins is the result of a re.match or re.search operation
            if earned_coins is not None:
                earned_coins = int(earned_coins.group(1).replace(',', ''))
            else:
                logger.error("Failed to parse earned coins.")
                # Handle the error appropriately, e.g., by setting a default value or raising an exception
                earned_coins = 0


            if has_item:
                # Looking for the span that contains the text indicating the item received
                item_received_span = soup.find('span', string=lambda text: 'retrieved a' in text if text else False)

                # Extracting the text of the next strong tag which should contain the name of the item received
                if item_received_span:
                    item_received = item_received_span.find_next('strong').text
                else:
                    item_received = "Unknown Item"
                logger.info(f'[{count}] [CATCHED!] Rarity: {pokemon_rarity} {emoji} | Pokemon: {pokemon_name} | Earned Coins: {earned_coins} | Item: {item_received}')
                return
            
            # Print the Pokemon name, rarity, and earned coins in one line
            logger.info(f'[{count}] [CATCHED!] Rarity: {pokemon_rarity} {emoji} | Pokemon: {pokemon_name} | Earned Coins: {earned_coins}')
            return
        else:
            logger.info(f'[{count}] [ESCAPED!] Rarity: {pokemon_rarity} {emoji} | Pokemon: {pokemon_name}')
            return
       
    def buy_balls(self, inventory):
        time.sleep(5)
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
    
    def open_lootbox(self, inventory):
        for item in inventory:
            # Check if the item name is pokecoin
            if item["name"] == "lootbox":
                # Update pokecoin count
                lootboxes = item["count"]
                if lootboxes > 10:
                    time.sleep(3)
                    self.write(";lb all")
                break      
    
    def print_initial_message(self):
        logger.warning("[Autplay settings] AutoBuy enabled: " + str(ENABLE_AUTO_BUY_BALLS))
        logger.warning("[Autplay settings] AutoLootbox enabled: " + str(ENABLE_AUTO_LOOTBOX))
        logger.warning("[Autplay settings] AutoRelease enabled: " + str(ENABLE_AUTO_RELEASE_DUPLICATES))
        logger.warning("[Autplay settings] AutoEgg enabled: " + str(ENABLE_AUTO_EGG_HATCH))
        logger.warning("[Autplay Advice] you can pause the bot by pressing 'p' in the console")
        logger.warning("[Autplay Advice] you can resume the bot by pressing 'enter' in the console")
        logger.warning("[Autplay Advice] you can stop the bot by pressing 'ctrl + c' in the console")
        logger.warning("="*60 + "\n")      

    def play(self):
        
        self.print_initial_message()
        
        #Initial commands
        self.write(";daily")
        time.sleep(4)
        self.write(";quest") 
        time.sleep(4)
        catch_counter = load_catch_counter()
        while True:
            
            # Check if user pressed 'p' to pause the execution
            if msvcrt.kbhit() and msvcrt.getch().decode('utf-8') == 'p':
                logger.warning('Execution paused. Press enter to continue...')
                input("Execution paused. Press enter to continue...")
                
            
            sleep_time = random.randint(7, 10)
            # sleep_time = 7
            self.write(";p")
            
            pokemeow_element_response = self.get_last_element_by_user("PokéMeow", timeout=30)
            
            if pokemeow_element_response is None:
                logger.error('No response from PokéMeow, trying again...')
                continue
            
            if "A wild Captcha appeared!" in pokemeow_element_response.text:
                logger.warning('Captcha detected')
                self.solve_captcha(pokemeow_element_response)
                continue
                
            if "Please wait" in pokemeow_element_response.text:
                logger.info('Please wait...')
                time.sleep(1.5)
                continue
            
            info_json = self.get_spawn_info(pokemeow_element_response)
            info = json.loads(info_json)
            
            rarity = info["Rarity"]
            ball = POKEMON_DICTIONARY.get(rarity)
            has_item = info["Item"]
            #Try to catch the pokemon
            if has_item and rarity not in "Legendary" and rarity not in "Shiny":
                self.click_on_ball("ultraball")
            else:
                if info["Name"] in pokeball_for_pokemon:
                    ball = pokeball_for_pokemon[info["Name"]]
                    logger.info(f"🔴 Pokemon '{info['Name']}' found in the dictionary. Using {ball}...")
                    self.click_on_ball(ball)
                else:
                    self.click_on_ball(ball)
            
            
            # Wait for the text of the element to change
            catch_status_element = self.wait_for_element_text_to_change(pokemeow_element_response)
            catch_counter += 1
            save_catch_counter(catch_counter)
            self.get_catch_result(info_json, catch_counter, catch_status_element)
            
            if ENABLE_AUTO_BUY_BALLS:
                if info["Balls"]["Pokeballs"] <= 1 or info["Balls"]["Greatballs"] <= 1:
                    inventory = self.get_inventory()
                    self.buy_balls(inventory)
            
            
            
            if catch_counter % 50 == 0:
                #Check inventory
                logger.info("Checking inventory...")
                inventory = self.get_inventory()
                if ENABLE_AUTO_LOOTBOX:
                    self.open_lootbox(inventory)
                
                if ENABLE_AUTO_EGG_HATCH:
                    egg_status = Inventory.get_egg_status(self.get_last_message_from_user("PokéMeow"))
                    if egg_status["can_hatch"]:
                            time.sleep(3)
                            logger.info("🐣 Hatching egg...")
                            self.write(";egg hatch")
                            hatch_element = self.get_last_element_by_user("PokéMeow", timeout=30)
                            # self.get_hatch_result(hatch_element)
                            
                    # Check if can hatch or hold egg
                    poke_egg_count = next((item['count'] for item in inventory if item['name'] == 'poke_egg'), None)
                    if poke_egg_count > 0:
                        if egg_status["can_hold"]:
                            time.sleep(3)
                            logger.info("🥚 Holding egg...")
                            self.write(";egg hold")
            
            #Writes quest and release duplicates every 100 catches
            if catch_counter % 100 == 0:
                time.sleep(3)
                self.write(";quest")
                # if ENABLE_AUTO_RELEASE_DUPLICATES:
                #     time.sleep(4.5)
                #     self.write(";r d")
            time.sleep(sleep_time)

    
    
    