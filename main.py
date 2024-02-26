from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import uuid
from selenium.webdriver.common.by import By
import requests
from dotenv import load_dotenv
import json



load_dotenv()

DISCORD_EMAIL = os.getenv('DISCORD_EMAIL')
PASSWORD = os.getenv('PASSWORD')
CHANNEL = os.getenv('CHANNEL')
POKEMON_DICTIONARY = json.loads(os.getenv('POKEMON_DICTIONARY'))
PREDICT_CAPTCHA_URL = os.getenv('PREDICT_CAPTCHA_URL')
DRIVER_PATH = os.getenv('DRIVER_PATH')
API_KEY = os.getenv('API_KEY')

class Main:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None

    def start_driver(self):
        self.driver = webdriver.Chrome(executable_path=self.driver_path)

    def navigate_to_page(self, url):
        if self.driver is not None:
            self.driver.get(url)
        else:
            print("Driver not started. Call start_driver first.")

    def quit_driver(self):
        if self.driver is not None:
            self.driver.quit()
        else:
            print("Driver not started. Nothing to quit.")
            
    def login(self, email, password):
        time.sleep(5)
        self.driver.find_element(
            "xpath", "//input[@class='inputDefault__80165 input_d266e7 inputField__79601']").send_keys(email)
        self.driver.find_element(
            "xpath", "//input[@class='inputDefault__80165 input_d266e7']").send_keys(password)
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
            print(f'📂 Number of images in captcha folder: {len(files)}')
            
            
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

            print("🚀 Sending image...")

            # Make the POST request and get the response
            response = requests.post(url, files=files, headers=headers)

        # If the request was successful, print the number from the response
        if response.status_code == 200:
            print("✅ Image sent successfully!")
            return response.json()["number"]
        else:
            print("❌ Failed to send image")
    
    def solve_captcha(self):
        resp = self.get_captcha()
        print(f'🔒 captcha response: {resp}')git
        self.write(resp)
        time.sleep(4)
                
        pokemeow_last_message = self.get_last_message_by_user("PokéMeow")
        if "Thank you" in pokemeow_last_message:
            print('🔓 Captcha solved!')
            return
        else:
            print('❌ Captcha failed!')
            print('❌ Trying again!')
            self.solve_captcha()

    
    def write(self, msg):
        span = self.driver.find_element("xpath", "//span[@class='emptyText_c03d90']")
        ActionChains(self.driver).send_keys_to_element(span, Keys.BACK_SPACE*20).send_keys_to_element(span, msg).perform()
        ActionChains(self.driver).send_keys_to_element(span, Keys.ENTER).perform()
 
    def wait_for_solve_captcha(self):
        # resp = self.get_captcha()
        print(f'🔒 Waiting for you to solve captcha... ')
        time.sleep(4)
                
        pokemeow_last_message = self.get_last_message_by_user("PokéMeow")
        if "Thank you" in pokemeow_last_message:
            print('🔓 Captcha solved!')
            return
        else:
            self.wait_for_solve_captcha()
                    
    def play(self):
        time.sleep(4)
        while True:
            sleep_time = 6.5
            self.write(";p")
            pokemeow_last_message = self.get_last_message_by_user("PokéMeow")
            time.sleep(3)   
            texto = self.driver.find_elements(
                "xpath", "//span[@class='embedFooterText_dc937f']")[-1].text

            arraytext = texto.split()
            
            rarity = arraytext[0]

            ball = POKEMON_DICTIONARY.get(rarity)

            if ball == None:
                # Please wait
                pokemeow_last_message = self.get_last_message_by_user("PokéMeow")
                if "Please wait" in pokemeow_last_message:
                    sleep_time = 0.5
                else:
                    self.solve_captcha()
                    sleep_time = 1
                
            else:
                (self.driver.find_elements("css selector",f'img[alt="{ball}"]')[-1].click())
            
            time.sleep(sleep_time)

        pass

if __name__ == "__main__":
    print('🚀 Starting bot...')
    main = Main(DRIVER_PATH)
    main.start_driver()
    main.navigate_to_page("https://discord.com/login")
    main.login(DISCORD_EMAIL,PASSWORD)
    main.navigate_to_page(CHANNEL)
    main.play()
    
    
    