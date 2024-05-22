import requests
import os
import json
import re
import csv
import sys

ROOT_URL = "http://biorisk-frontend.eu-west-1.elasticbeanstalk.com"
USERNAME = "anewman"
PASSWORD = "Ta1sh1ng"

CATEGORY_ENDPOINT = "https://prod.eu-west-1.prometheus-prod.sd.co.uk/content/v2/menu"

class BioriskScraper():
    def __init__(self):
        self.categories = []
        self.session = requests.session()
        self.session.auth = (USERNAME, PASSWORD)
        self.create_folder('results')
    
    def create_folder(self, path):
        try:
            if not os.path.exists(path):
                os.mkdir(path)
        except:
            pass

    def extract_property(self, property):
        print(f"   --- PROPERTY : {property["id"]}")
        resp = self.session.get(f"{ROOT_URL}/v1/properties/{property["id"]}")
        if resp.status_code != 200:
            return
        property = resp.json()
        jobs = property["jobs"]
        property["jobs"] = []
        for job in jobs:
            job["property"] = property
            self.save_job(job)

    def extract_clent(self, client):
        print(f"###### CLIENT : {client["id"]} :{client["name"]}")
        resp = self.session.get(f"{ROOT_URL}/api/v1/clients/{client["id"]}")
        if resp.status_code != 200:
            return
        client = resp.json()
        properties = client["properties"]
        for property in properties:
            self.extract_property(property)

    def get_clients(self):
        resp = self.session.get(f"{ROOT_URL}/api/v1/clients")
        if resp.status_code != 200:
            return None
        return resp.json()
    
    def get_job(self, jobID):
        resp = self.session.get(f"{ROOT_URL}/v1/jobs/{jobID}")
        if resp.status_code != 200:
            return None
        return resp.json()

    def save_job(self, job):
        print(f"     * JOB : {job["id"]}")
        job_file = f"./results/{job["id"]}.json" 
        if os.path.exists(job_file):
            return
        with open(job_file, 'w', encoding="utf-8") as f:
            json.dump(job, fp=f, indent='\t')
        
    def start(self):
        clients = self.get_clients()
        for client in clients:
            self.extract_clent(client)
                

def main():
    extractor = BioriskScraper()
    extractor.start()

    
if __name__ == "__main__":
    main()
