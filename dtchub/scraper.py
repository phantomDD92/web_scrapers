import os
import requests
import json

MAIN_URL = ""

class Scraper():

    def __init__(self):
        self.session = requests.Session()
        self.categories = dict()
        self.images = dict()
        self.create_folder('results')
        self._load_main_json()
    
    def _load_main_json(self):
        data = dict()
        with open("./main.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        for elem in data["mainCategories"]:
            key = str(elem["mainCategoryId"])
            self.categories[key] = elem["mainCategoryName"]
        for elem in data["subCategories"]:
            key = str(elem["subCategoryId"])
            pkey = str(elem["mainCategoryId"])
            self.categories[key] = self.categories[pkey] + "|" + elem["subCategoryName"]
        for elem in data["images"]:
            key = str(elem["productId"])
            self.images[key] = elem["productImageUrl"]
    
    def create_folder(self, path):
        try:
            if not os.path.exists(path):
                os.mkdir(path)
        except:
            pass
    
    def _login(self):
        resp = self.session.post("https://dtchub-api.azurewebsites.net/api/auth/token", {
            "email": "chris@greentriangleuk.com", 
            "password": "Cy@123456789"}
        )
        if resp.status_code != 200:
            print("login failed")
            exit()
        result = resp.json()
        self.session.headers.update({
            'Authorization': f'Bearer {result["token"]}'
        })
    
    def _get_product(self, productId):
        resp = self.session.get(f"https://dtchub-api.azurewebsites.net/api/product/00000001/product/{productId}/v2")
        if resp.status_code != 200:
            return None
        return resp.json()
    
    def start(self):
        products = []
        with open('./products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        self._login()
        for elem in products:
            info = self._get_product(elem["productId"])
            print(info)
            break


def main():
    scraper = Scraper()
    scraper.start()

    
if __name__ == "__main__":
    main()