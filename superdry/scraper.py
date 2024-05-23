import requests
import os
import json
import re
import csv
import sys

ROOT_URL = "https://www.screwfix.com"
MAIN_URL = "https://www.screwfix.com/c/electrical-lighting/cat840780"
HREF_PATTERN = r"https://media.screwfix.com/is/image/ae235/([^?]+)\?[^&]+&wid=257&hei=257&.+"
PAGE_SIZE = 10

CATEGORY_ENDPOINT = "https://prod.eu-west-1.prometheus-prod.sd.co.uk/content/v2/menu"

class SuperDryExtractor():
    def __init__(self):
        self.categories = []
        self.session = requests.session()
        self.create_folder('results')
    
    def create_folder(self, path):
        try:
            if not os.path.exists(path):
                os.mkdir(path)
        except:
            pass
    def has_product(self, product):
        if os.path.exists(f"./results/{product['skuCode']}.json"):
            return True
        return False
    
    def save_product(self, product):
        with open(f"./results/{product['skuCode']}.json", 'w', encoding="utf-8") as f:
            json.dump(product, fp=f, indent='\t')

    def make_td(self, key, value):
        return f"<tr><td>{key}</td><td align=\"center\">{value}</td></tr>"
    
    def make_specification(self, result):
        try :
            tbodyContent = ""
            tbodyContent += self.make_td("Color", result["colour"]["description"].capitalize())
            sizeValues = [x["name"] for x in result["availableSizes"]]
            tbodyContent +=  self.make_td("Size", ", ".join(sizeValues))
            modelValues = []
            for key in result["model"]:
                modelValues.append(f"{key}:{result["model"][key]}") 
            tbodyContent +=  self.make_td("Model", " | ".join(modelValues))
            for meterial in result["specification"]["materials"]:
                part = meterial["part"]
                fabricValues = [ f"{x["fabric"]} {x["percentage"]}%" for x in meterial["fabrics"]]
                tbodyContent += self.make_td(part, ", ".join(fabricValues))
            for key in result["specification"]["cleaning"]:
                tbodyContent += self.make_td(key.capitalize(), result["specification"]["cleaning"][key])
            return f"<table><thead><tr><th colspan=\"2\" align=\"left\">Specification</th></tr></thead><tbody>{tbodyContent}</tbody></table>"
        except Exception as e:
            print(e)
            return ""
        
    def save_images(self, product, urls):
        images = []
        for i in range(len(urls)):
            url = urls[i]
            resp = self.session.get(url)
            with open(f"./results/{product["skuCode"]}_{i}.jpg", 'wb') as f:
                f.write(resp.content)
            images.append(f"{product["skuCode"]}_{i}.jpg")
        return images

    def extract_product(self, productinfo):
        try:
            print(f"@ {productinfo.get("id", "")}")
            resp = self.session.get("https://prod.eu-west-1.prometheus-prod.sd.co.uk/data-service/product-detail/v1/", params={
                "productId": productinfo.get("id", ""), 
                "siteId": 3
            })
            if resp.status_code != 200:
                return
            result = resp.json()
            product = dict()
            product["name"] = result.get("name", "")
            catpath = result.get("canonicalCategoryPath", "")
            categories = [x.capitalize() for x in catpath.split("/")]
            product["categories"] = categories[1:]
            product["description"] = f"<div>{result.get("description", "")}</div>"
            product["salePrice"] = result.get("price", 0)
            product["brand"] = "Superdry"
            sizeInfo = result.get("availableSizes", [])[0]
            product["skuCode"] = sizeInfo.get("sku", "")
            product["moreInfo"] = self.make_specification(result)
            if self.has_product(product):
                return
            product["images"] = self.save_images(product, result["media"])
            self.save_product(product)
        except Exception as e:
          print(e)
          pass
   
    
    def load_categories(self):
        resp = self.session.get(CATEGORY_ENDPOINT, params={"siteId": 3})
        if resp.status_code != 200:
            return
        data = resp.json()
        self.categories = data.get("main", [])
    
    def load_products(self, category):
        print(f"$ {category.get("text", "")} : {category.get("url", "")}")
        resp = self.session.get("https://prod.eu-west-1.prometheus-prod.sd.co.uk/content/v2/page", params={
            "siteId": 3,
            "path": category.get("url", "")
        })
        if resp.status_code != 200:
            print("!1")
            return
        result = resp.json()
        resp = self.session.get("https://prod.eu-west-1.prometheus-prod.sd.co.uk/data-service/product-list/v1/", params={
            "type": result.get("contentType", ""),
            "identifier": result.get("categoryId", ""),
            "path": result.get("path", ""),
            "siteId": 3,
            "limit": PAGE_SIZE,
            "offset": 0,
            "page": 1,
            "scrollYPos": 0
        })
        if resp.status_code != 200:
            return
        res = resp.json()
        # if res.get("meta", None) == None:
        #     return
        # total = res["meta"].get("totalProducts", PAGE_SIZE)
        # resp = self.session.get("https://prod.eu-west-1.prometheus-prod.sd.co.uk/data-service/product-list/v1/", params={
        #     "type": result.get("contentType", ""),
        #     "identifier": result.get("categoryId", ""),
        #     "path": result.get("path", ""),
        #     "siteId": 3,
        #     "limit": total,
        #     "offset": 0,
        #     "page": 1,
        #     "scrollYPos": 0
        # })
        # if resp.status_code != 200:
        #     return
        # res = resp.json()
        for product in res.get("products", []):
            self.extract_product(product)

    def extract_category(self, category):
        subcats = category.get("items", [])
        if len(subcats) > 0:
            print(f"# {category.get("text", "")} : {category.get("url", "")}")
            for item in subcats:
                self.extract_category(item)
        else:
            self.load_products(category)
        
    def start(self):
        self.load_categories()
        for item in self.categories:
            self.extract_category(item)
        pass

def main():
    extractor = SuperDryExtractor()
    extractor.start()

    
if __name__ == "__main__":
    main()
