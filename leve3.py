import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

GOOGLE_SHEETS_API_KEY = os.environ.get("GOOGLE_SHEETS_API_KEY")

driver = webdriver.Chrome()

driver.get("https://www.olx.ua/uk/nedvizhimost/?currency=UAH")

real_estate = driver.find_elements(By.CLASS_NAME, 'css-1sw7q4x')

real_estate_list = []
for value in real_estate:
    yes = value.text.split("\n")
    try:
        yes.remove("ТОП")
    except ValueError:
        pass
    real_estate_list.append(yes)

print(real_estate_list)

import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# change this by your sheet ID
SAMPLE_SPREADSHEET_ID_input = '1OSD8NJHLIkB__tt0O4eeMO4RBNt71YuWigT858H_wC8'

# change the range if needed
SAMPLE_RANGE_NAME = 'A1:AA1000'


def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    # print(SCOPES)

    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        # return service
    except Exception as e:
        print(e)
        # return None


# change 'my_json_file.json' by your downloaded JSON file.
Create_Service('credentials1.json', 'sheets', 'v4', ['https://www.googleapis.com/auth/spreadsheets'])


def Export_Data_To_Sheets():
    response_date = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
        valueInputOption='RAW',
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=real_estate)
    ).execute()
    print('Sheet successfully Updated')


Export_Data_To_Sheets()