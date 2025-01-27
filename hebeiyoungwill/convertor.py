import sys
import requests
import os
import json
from lxml import etree

class ProductConvertor():
    def __init__(self, folder):
        self.result_folder = folder
        self.session = requests.session()
        
    def start(self):
        upload_count = 0
        skip_count = 0
        # if not self.login():
        #     return
        # load all json files
        json_files = [ each for each in os.listdir(self.result_folder) if each.endswith('.json')]
        for json_file in json_files:
            # load product data
            with open(os.path.join(self.result_folder, json_file), 'r', encoding='utf-8') as f:
                product = json.load(f)
            # if already uploaded, skip uploading
            description = product["description"]
            parser = etree.HTMLParser()
            tree = etree.fromstring(description, parser)
            elements = tree.xpath(f"//h2/strong/span[contains(text(), 'Product details')]")
            if len(elements) > 0 :
                print(json_file)
                element = elements[0].getparent().getparent()
                next = element.getnext()
                parent = element.getparent()
                parent.remove(element)
                parent.remove(next)
                body = tree.find('body')
                output = ''.join(etree.tostring(element).decode() for element in body)
                product["description"] = output.replace("\n", "").strip()
                product["moreInfo"] = ("<div>" + etree.tostring(element).decode().strip() + etree.tostring(next).decode().strip() + "</div>").replace("\n", "")
                with open(os.path.join("results1", json_file), 'w', encoding='utf-8') as f:
                    json.dump(product, f, indent='\t')
                os.rename(os.path.join(self.result_folder, json_file), os.path.join("orgs", json_file))
                upload_count += 1
                # break
            
            # mark product uploaded
        print(f"\n{upload_count} products updated.\n{skip_count} products skipped.\n")

def main():
    if len(sys.argv) != 2:
        folder = 'results'
    else:
        folder = int(sys.argv[1])
    if not os.path.exists(folder):
        print('Data folder does not exist.')
        exit()
    extractor = ProductConvertor(folder)
    extractor.start()
    
if __name__ == "__main__":
    main()
