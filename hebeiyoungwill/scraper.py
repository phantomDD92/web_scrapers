import requests
import os
import json
import re
from lxml import html

BASE_URL = "https://hebeiyoungwill.com"

class SiteExtractor():

    def __init__(self):
        self.product_count = 0
        self.categories = []
        self.session = requests.session()
        self.create_folder('results')
    
    def create_folder(self, path):
        try:
            if not os.path.exists(path):
                os.mkdir(path)
        except:
            pass
    
    def save_product(self, product):
        with open(f"./results/{product['id']}.json", 'w', encoding="utf-8") as f:
            json.dump(product, fp=f, indent='\t')
        
    def save_image(self, path, name):
        try:
            if os.path.exists(f"./results/{name}"):
                print(f'--- IMAGE: {name}')
                return True
            resp = self.session.get(f'http:{path}')
            with open(f"./results/{name}", 'wb') as f:
                f.write(resp.content)
            print(f'+++ IMAGE: {name}')
            return True
        except Exception as e:
            print("$$$ ERROR: download image({name}) failed, ", e)
            return False

    def remove_links(self, html_content):
        # Regular expression to remove <a> tags but keep their content
        pattern = r"<a [^>]*>(.*?)</a>"
        # Replace the matched <a> tags with their content
        modified_html = re.sub(pattern, r"\1", html_content)
        return modified_html

    def get_product(self, category, path):
        try:
            resp = self.session.get(f'{BASE_URL}{path}')
            if not resp.ok:
                print(f'$$$ ERROR : get product for {path} failed with response {resp.status_code}')
                return
            product = dict()
            tree = html.fromstring(resp.text)
            script_tag = tree.cssselect("script[type='application/ld+json']")[0]
            json_str = script_tag.text_content()
            json_data = json.loads(json_str)
            self.product_count += 1
            product["id"] = json_data.get("productID")
            product["name"] = json_data.get("name")
            print(f'+++ PRODUCT {self.product_count}: {product["name"]}')
            product["brand"] = json_data.get("brand").get("name")
            product["categories"] = category["categories"]
            product["salePrice"] = json_data.get("offers")[0].get("price")
            product["skuCode"] = json_data.get("sku")
            desc_tag = tree.cssselect("div.product-description-toggle > div")[0]
            product["description"] = self.remove_links(html.tostring(desc_tag, pretty_print=True).decode())
            # product["description"] = json_data.get("description")
            product["moreInfo"] = ""
            images = []
            image_tags = tree.cssselect("flickity-carousel > div.product__media-item > div > img")
            count = 0
            for image_tag in image_tags:
                image_path = image_tag.get("src")
                image_name = f'{product["id"]}_{count}.jpg'
                count += 1
                if self.save_image(image_path, image_name):
                    images.append(image_name)
            product["images"] = images
            self.save_product(product)
        except Exception as e:
            print(f'$$$ ERROR : get product for {path} failed with error {str(e)}')

    def get_products_for_page(self, category, page):
        print(f'### CATEGORY PAGE {page} FOR {category["name"]}')
        print(f'{BASE_URL}{category["path"]}?page={page}')
        try:
            resp = self.session.get(f'{BASE_URL}{category["path"]}?page={page}')
            if not resp.ok:
                print(f'$$$ ERROR : get products for {category["name"]} failed with response {resp.status_code}')
                return [], False
            product_paths = []
            tree = html.fromstring(resp.text)
            product_tags = tree.cssselect("div.product-item__info > div.product-item-meta > a.product-item-meta__title")
            for product_tag in product_tags:
                path = product_tag.get("href")
                product_paths.append(path)
            next_page_tags = tree.cssselect("page-pagination > nav > a[rel='next']")
            has_next = len(next_page_tags) > 0
            return product_paths, has_next
        except Exception as e:
            print("$$$ ERROR :", str(e))
            return [], False
    
    def get_products_for_category(self, category):
        page = 1
        has_next = True
        while has_next:
            product_paths, has_next = self.get_products_for_page(category, page)
            page += 1
            for product_path in product_paths:
                self.get_product(category, product_path)
            #     break
            # break

    def get_categories(self):
        try:
            resp = self.session.get(BASE_URL)
            if not resp.ok:
                print(f'$$$ ERROR : get categories failed with response {resp.status_code}')
                return None
            categories = []
            tree = html.fromstring(resp.text)
            top_cat_tags = tree.cssselect('desktop-navigation > ul > li.has-dropdown')
            last_top_cat_id = len(top_cat_tags)
            id = 1
            for top_cat_tag in top_cat_tags:
                if id == last_top_cat_id:
                    continue
                id += 1
                top_cat_link_tag = top_cat_tag.cssselect("a")[0]
                top_cat_name = str(top_cat_link_tag.text_content()).strip()
                sub_cat_tags = top_cat_tag.cssselect("ul > li > a")
                for sub_cat_tag in sub_cat_tags:
                    cat = dict()
                    cat["name"] = str(sub_cat_tag.text_content()).strip()
                    cat["categories"] = [top_cat_name, cat["name"]]
                    cat["path"] = sub_cat_tag.get("href")
                    categories.append(cat)
            return categories
        except Exception as e:
            print("$$$ ERROR :", str(e))
            return None

    def start(self):
        categories = self.get_categories()
        for category in categories:
            self.get_products_for_category(category)
            # break
        

def main():
    extractor = SiteExtractor()
    extractor.start()

    
if __name__ == "__main__":
    main()
