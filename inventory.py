from bs4 import BeautifulSoup
import json
from selenium.webdriver.remote.webelement import WebElement

class Inventory:
    
    @staticmethod
    def get_egg_status(html_content):
        # Check if html_content is a WebElement
        if isinstance(html_content, WebElement):
            html_content = html_content.get_attribute('outerHTML')

        soup = BeautifulSoup(html_content, 'html.parser')
        # Check for READY TO HATCH
        ready_to_hatch = soup.find(string="[READY TO HATCH!]")
        if ready_to_hatch:
            return {"can_hatch": True, "can_hold": False}

        # Check for holding egg with counter
        counter = soup.find(string=lambda text: "[COUNTER:" in text)
        if counter:
            return {"can_hatch": False, "can_hold": False}

        # Check for no egg and no holding
        eggs = soup.find_all(string=lambda text: "x Eggs" in text)
        for egg in eggs:
            if "0x Eggs" in egg:
                return {"can_hatch": False, "can_hold": True}

        # If none of the conditions above are met, we cannot determine the status
        return {"can_hatch": False, "can_hold": True}


    @staticmethod
    def get_inventory(html_content):
        import re
         # Function to check if a tag contains a partial class name
        def contains_partial_class(partial):
            return re.compile(".*" + partial + ".*")
    
        # Check if html_content is a WebElement
        if isinstance(html_content, WebElement):
            html_content = html_content.get_attribute('outerHTML')

        # print(html_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Initialize a list to store each item in a flat structure
        items_list = []
        
        # Find all categories
        categories = soup.find_all("div", class_="embedFieldName_d42d0c")
        categories = soup.find_all("div", class_=contains_partial_class("embedFieldName"))
        
        for category in categories:
            category_name = category.get_text(strip=True)
            # item_container = category.find_next_sibling("div", class_="embedFieldValue_f2dcec")
            item_container = category.find_next_sibling("div", class_=contains_partial_class("embedFieldValue"))

            if item_container:
                for item in item_container.find_all("span", class_=contains_partial_class("emojiContainer")):
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

# # Test the Inventory class using index.html file as html_content    
# html_content = ""
# with open("index.html", "r") as file:
#     html_content = file.read()


# print(Inventory.get_egg_status(html_content))
# print(Inventory.get_inventory(html_content))
