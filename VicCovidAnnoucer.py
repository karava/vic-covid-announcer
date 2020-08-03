#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
from datetime import date
import json
import os
from twilio.rest import Client
import config
URL = "https://www.dhhs.vic.gov.au/coronavirus"
OUTPUT_FILE = "./output/output.txt"
account_sid = config.TWILIO_ACCOUNT_SID
auth_token = config.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

def checkCurrentNumbersFromWeb():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(class_='covid-number-box')
    comment = results.find_all('p')
    comment = comment[0].text
    updated_date = soup.find(class_='updated')
    updated_date = updated_date.find("span").next_sibling
    number = results.find(class_='numbers').text
    print("[DEBUG] Latest from website:", updated_date, number)
    return comment, updated_date, number

def check_if_updated(updated_date):
    if os.path.getsize(OUTPUT_FILE) == 0:
        print("[DEBUG] Empty file")
        return False
    with open(OUTPUT_FILE, 'r') as f:
        data = json.loads(f.read())
        if updated_date in data.keys() and 'VIC' in data[updated_date].keys():
            print("[DEBUG] Already up-to-date")
            return True
        else:
            print("[DEBUG] Need to update")
            return False

def write_to_file(updated_date, number):
    if os.path.getsize(OUTPUT_FILE) != 0:
        with open(OUTPUT_FILE, 'r') as f:
            data = json.loads(f.read())
    else:
        data = {}
    with open(OUTPUT_FILE, 'w') as f:
        data[updated_date] = {}
        data[updated_date]["VIC"] = number
        json.dump(data,f)
        print("[DEBUG] Update saved to file")

def sendSms(comment, number):
    sms_body = f"CORONVIRUS UPDATE\n"
    sms_body += f"{comment}\n VIC: {number}"
    client.messages.create(body=sms_body, from_=config.FROM_NUMBER, to=config.TO_NUMBER)
    print("[DEBUG] Sending SMS update")

def main():
    comment, updated_date, number = checkCurrentNumbersFromWeb()
    if check_if_updated(updated_date) == False:
        write_to_file(updated_date, number)
        sendSms(comment, number)

main()

os.path.getsize(OUTPUT_FILE)



