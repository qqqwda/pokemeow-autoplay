from httpcore import TimeoutException
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
logger = Logger.getInstance().get_logger()
captcha_service = CaptchaService()

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


    def write(self, msg):
        span = self.driver.find_element("xpath", "//span[@class='emptyText_c03d90']")
        ActionChains(self.driver).send_keys_to_element(span, Keys.BACK_SPACE*20).send_keys_to_element(span, msg).perform()
        ActionChains(self.driver).send_keys_to_element(span, Keys.ENTER).perform()
    
    def get_captcha(self):
        
        div_element = self.get_last_element_by_user("PokéMeow")
        
        # Find the first a element within the div element
        a_element = div_element.find_elements(By.TAG_NAME, "a")[-1]

        # Now you can get the href attribute or do whatever you need with the a element
        href = a_element.get_attribute("href")
        img_path = self.download_captcha(href)
        
        return self.send_image(img_path)
    
    
    def get_last_element_by_user(self, username, timeout=30) -> WebElement:
        try:
            # Wait for a new message from the user to appear
            WebDriverWait(self.driver, timeout).until(
                lambda driver: self.check_for_new_message(username)
            )
            
            logger.info(f"Message from {username} found.")

            # Fetch all message elements
            messages = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'messageListItem__6a4fb')]")

            # Iterate over messages in reverse to find the last message from the user
            for message in reversed(messages):
                user_elements = message.find_elements(By.XPATH, ".//span[contains(@class, 'username_d30d99')]")
                if user_elements:
                    user_element = user_elements[-1]
                    if username in user_element.text:
                        # Return the message element
                        return message

            logger.info(f"Message from {username} not found.")
            return None

        except TimeoutException:
            logger.info(f"Message from {username} not found. Timeout exceeded.")
            return None

        except NoSuchElementException:
            logger.info("Error: Unable to locate element.")
            return None

    def check_for_new_message(self, username):
        # Fetch all message elements
        messages = self.driver.find_elements(By.XPATH, "//li[contains(@class, 'messageListItem__6a4fb')]")

        # Check if the last message is from the user
        if messages:
            last_message = messages[-1]
            user_elements = last_message.find_elements(By.XPATH, ".//span[contains(@class, 'username_d30d99')]")
            if user_elements:
                user_element = user_elements[-1]
                return username in user_element.text

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
                    logger.error("❌ Element is no longer attached to the DOM")
                    return None

                # Wait before checking the text of the element again
                time.sleep(1)

            # If the timeout is reached without the text of the element changing, return None
            logger.warning("⏰ Timeout reached without text change")
            return None

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    
    def solve_captcha(self, element):
        
        pokemeow_last_message = self.wait_for_element_text_to_change(element)
        
        if "Thank you" in pokemeow_last_message.text:
            logger.info('🔓 Captcha solved!')
            return
        else:
            logger.info('❌ Captcha failed!')
            logger.info('❌ Trying again!')
            self.solve_captcha(pokemeow_last_message)
    
    
    def get_spawn_info(self, element):
        
        pokemon_info = {}
        
        # Parse the HTML content
        soup = BeautifulSoup(element.get_attribute('outerHTML'), "html.parser")
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
        # time.sleep(3)
        # self.write(";daily")
        # time.sleep(4)
        # self.write(";quest")
        time.sleep(4)
        while True:
            sleep_time = random.randint(9, 12)
            sleep_time = 7
            self.write(";p")
            
            pokemeow_element_response = self.get_last_element_by_user("PokéMeow", timeout=30)
            
            if pokemeow_element_response is None:
                logger.info('❌ No response from PokéMeow, trying again...')
                continue
            
            if "A wild Captcha appeared!" in pokemeow_element_response.text:
                logger.info('🔒 Captcha detected')
                self.solve_captcha(pokemeow_element_response)
                continue
                
            if "Please wait" in pokemeow_element_response.text:
                logger.info('⏳ Please wait...')
                time.sleep(1.5)
                continue
            
            info_json = self.get_spawn_info(pokemeow_element_response)
            
            logger.info(info_json)
            # Wait for the text of the element to change
            new_text = self.wait_for_element_text_to_change(pokemeow_element_response)
            
            # get last element edited by PokéMeow
            
            
            
            # if "Please wait" in pokemeow_last_message:
            #     #Go back to the start of the loop
            #     time.sleep(1)
            #     continue
            
            # if "TYPE" in pokemeow_last_message.lower():
            #     logger.info('🔒 Captcha detected!')
            #     self.solve_captcha()
            #     continue
                    
            # texto = self.driver.find_elements(
            #     "xpath", "//span[@class='embedFooterText_dc937f']")[-1].text
            
            # arraytext = texto.split()
            
            # rarity = arraytext[0]

            # ball = POKEMON_DICTIONARY.get(rarity)

            # if ball == None:
            #     self.solve_captcha()
            #     sleep_time = 1
                
            # else:
            #     self.click_on_ball(ball)
                
            #     pokemon_info_json = self.get_pokemon_info()
            #     info = json.loads(pokemon_info_json)
            #     catch_counter += 1
            #     save_catch_counter(catch_counter)
            #     threading.Thread(target=self.get_catch_result, args=(pokemon_info_json,catch_counter,)).start()
                
            #     # Now you can access the elements of pokemon_info as a dictionary
                
            #     if info["Balls"]["Pokeballs"] <= 1 or info["Balls"]["Greatballs"] <= 1:
            #         inventory = self.get_inventory()
            #         self.buy_balls(inventory)
                
            #     if catch_counter % 25 == 0:
            #         self.write(";r d")
            #         time.sleep(4)
            #         inventory = self.get_inventory()
            #         self.open_lootbox(inventory)
                
            #     if catch_counter % 100 == 0:
            #         self.write(";quest")
            # # Save current catch count in memory
            
            time.sleep(sleep_time)

    
    
    