import sys
import requests
import os
import json
from dotenv import load_dotenv

API_ENDPOINT_ADDSKU = "/api/Sku/add-demo-sku"
API_ENDPOINT_LOGIN = "/api/Account/login"
API_ENDPOINT_ADDSKUIMAGE = "/api/Sku/add-sku-images"

class ProductUploader():
    def __init__(self, folder):
        self.result_folder = folder
        self.session = requests.session()
        self.api_root=os.getenv("API_ROOT")
        self.api_credential={
            "companyName": os.getenv("COMPANY_NAME"),
            "email": os.getenv("AGENCY_EMIAL"),
            "password": os.getenv("AGENCY_PASSWORD")
        }

    def login(self):
        headers = {'Content-Type': 'application/json'} 
        json_data = json.dumps(self.api_credential) 
        resp = self.session.post(f"{self.api_root}{API_ENDPOINT_LOGIN}", data=json_data, headers=headers)
        respData = resp.json()
        if resp.status_code == 200:
            self.token = respData.get("token")
            self.session.headers.update({'Authorization': 'Bearer ' + self.token})
            print("Login Success")
            return True
        print("--- ERROR : login : ", resp.status_code)
        return False
        
    def addSku(self, data):
        headers = {'Content-Type': 'application/json'} 
        json_data = json.dumps(data) 
        resp = self.session.post(f"{{self.api_root}}{API_ENDPOINT_ADDSKU}", data=json_data, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("data", None)
        print("--- ERROR : addSku : ", resp.status_code)
        return None

    def addSkuImages(self, skuId, imageNames):
        files= []
        imageNames.sort()
        # print(imageNames)
        for imageName in imageNames:
            if not os.path.exists(os.path.join(self.result_folder, imageName)):
                continue
            files.append(('Images', (imageName, open(os.path.join(self.result_folder, imageName), 'rb'),'image/jpeg')))
        resp = self.session.post(f"{{self.api_root}}{API_ENDPOINT_ADDSKUIMAGE}", files=files, params={"SkuId": skuId,})
        if resp.status_code == 200:
            return True
        print("--- ERROR : addSkuImage : ", resp.status_code)
        return False
    
    def upload(self, product):
        data = {
            "categories": product.get("categories", []),
            "skuCode": product.get("skuCode", ""),
            "name": product.get("name", ""),
            "description": product.get("description", ""),
            "salePrice": product.get("salePrice", "0"),
            "brand": product.get("brand", ""),
            "moreInfo": product.get("moreInfo", ""),
        }
        skuId = self.addSku(data)
        print("SKU ID: ", skuId)
        if not skuId:
            return False
        imageNames = product.get('images', [])
        if self.addSkuImages(skuId, imageNames):
            return skuId
        return None
        
    def start(self):
        upload_count = 0
        fail_count = 0
        skip_count = 0
        if not self.login():
            return
        # load all json files
        json_files = [ each for each in os.listdir(self.result_folder) if each.endswith('.json')]
        for json_file in json_files:
            # load product data
            with open(os.path.join(self.result_folder, json_file), 'r', encoding='utf-8') as f:
                product = json.load(f)
            # if already uploaded, skip uploading
            if product.get('Upload', False):
                print(f"# Product({product['skuCode']}) : Uploaded already!")
                skip_count += 1
                continue
            # if failed to upload, skip uploading
            skuId = self.upload(product)
            if skuId is None:
                print(f"$ Product({product['skuCode']}) : Failed to upload.")
                fail_count += 1
                continue
            print(f"# Product({product['skuCode']}) : {skuId} : Uploaded successfully!")
            upload_count += 1
            # mark product uploaded
            product['Upload'] = True
            with open(os.path.join(self.result_folder, json_file), 'w', encoding='utf-8') as f:
                json.dump(product, f)
            break
        print(f"\n{upload_count} products uploading.\n{fail_count} products failed.\n{skip_count} products skipped.\n")

def main():
    if len(sys.argv) != 2:
        folder = 'results'
    else:
        folder = int(sys.argv[1])
    if not os.path.exists(folder):
        print('Data folder does not exist.')
        exit()
    extractor = ProductUploader(folder)
    extractor.start()
    
if __name__ == "__main__":
    load_dotenv()
    main()
