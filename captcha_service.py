import os
import uuid
from selenium.webdriver.common.by import By
import requests
from logger import Logger
from dotenv import load_dotenv

logger = Logger(__name__).getInstance().get_logger()
load_dotenv()
PREDICT_CAPTCHA_URL = os.getenv('PREDICT_CAPTCHA_URL')
API_KEY = os.getenv('API_KEY')

class CaptchaService:
    
    @staticmethod 
    def download_captcha(href):
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
            
            return f"captchas/image_{image_id}.png"
        
        return None
    
    @staticmethod 
    def send_image(image_path):
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
                    response = requests.post(url, files=files, headers=headers, timeout=35)  # Wait up to 35 seconds

                    # If the request was successful, print the number from the response
                    if response.status_code == 200:
                        logger.info("✅ Image sent successfully!")
                        return response.json()["number"]
                    else:
                        logger.info("❌ Failed to send image")
                        # logger.info(f"❌ Message: {response.json()['messages']}")
                except requests.exceptions.Timeout:
                    logger.info("⏰ Request timed out, retrying...")

        logger.info("❌ Failed to send image after 3 attempts")