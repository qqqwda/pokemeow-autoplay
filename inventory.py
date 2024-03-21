from bs4 import BeautifulSoup
import json
from selenium.webdriver.remote.webelement import WebElement

class Inventory:
    
    @staticmethod
    def get_inventory(html_content):

        # Check if html_content is a WebElement
        if isinstance(html_content, WebElement):
            html_content = html_content.get_attribute('outerHTML')

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize a list to store each item in a flat structure
        items_list = []
        
        # Find all categories
        categories = soup.find_all("div", class_="embedFieldName_d42d0c")
        
        for category in categories:
            category_name = category.get_text(strip=True)
            item_container = category.find_next_sibling("div", class_="embedFieldValue__53d47")
            if item_container:
                for item in item_container.find_all("span", class_="emojiContainer__4a804"):
                    item_name = item.img['alt'] if item.img else "Unknown"
                    count_text = item.find_next_sibling("strong")
                    count = count_text.get_text(strip=True) if count_text else "0"
                    item_dict = {
                        "name": item_name. replace(":", "").lower(),
                        "count": int(count.replace(",", ""))
                    }
                    items_list.append(item_dict)
        
        # Convert the list of items to JSON
        items_json = json.dumps(items_list, indent=4)
        return items_json

# Test the Inventory class using index.html file as html_content    
# html_content = ""
# with open("index.html", "r") as file:
#     html_content = file.read()

# print(Inventory.get_inventory(html_content))

