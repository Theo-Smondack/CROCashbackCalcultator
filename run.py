import os
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.ttk import *

import requests.exceptions
from requests import Request, Session
from dotenv import load_dotenv
import json
import pandas as pd

load_dotenv()

root = Tk()
root.geometry('400x200')
root.title('CRO Cashback calculator')
dir_path = os.environ['HOME'] + os.getenv('DIR_PATH')
currency = os.getenv('CURRENCY')

url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
parameters = {
    "slug": "cronos",
    "convert": currency
}

headers = {
    "Accepts": "application/json",
    "X-CMC_PRO_API_KEY": os.getenv('API_KEY')
}

check_CSV_columns_names = ["Timestamp (UTC)", "Transaction Description", "Currency", "Amount", "To Currency",
                           "To Amount",
                           "Native Currency", "Native Amount", "Native Amount (in USD)", "Transaction Kind",
                           "Transaction Hash"]


def call_api():
    global cro_current_price
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        response.raise_for_status()
        if currency == "EUR":
            cro_current_price = json.loads(response.text)['data']['3635']['quote']['EUR']['price']
        elif currency == "USD":
            cro_current_price = json.loads(response.text)['data']['3635']['quote']['USD']['price']
        return cro_current_price
    except requests.exceptions.ConnectionError as errc:
        print('\033[91mError Connecting:', errc, '\033[0m')
    except requests.exceptions.HTTPError as httperr:
        print('\033[91mHTTPError:', httperr, '\033[0m')


def open_file():
    file = askopenfilename(initialdir=dir_path, filetypes=[('CSV Files', '*.csv')])
    f = open(file=file, mode='r')
    cro_amount = 0
    fiat_amount = 0
    symbol = "€" if currency == 'EUR' else "$"
    if file is not None:
        data = pd.read_csv(f)
        list_of_column_names = list(data.columns)
        if list_of_column_names == check_CSV_columns_names:
            for i, row in data.iterrows():
                kind = row['Transaction Kind']
                if row['Native Currency'] == currency:
                    fiat = row['Native Amount']
                else:
                    fiat = round(row['Native Amount (in USD)'], 2)
                if kind == "referral_card_cashback" or kind == "reimbursement" or kind == "crypto_earn_interest_paid":
                    cro_amount = cro_amount + row.Amount
                    fiat_amount = fiat_amount + fiat
            lbl.config(text="Total of CRO earned : " + str(cro_amount))
            lbl2.config(text="Total of " + currency + " saved : " + str(fiat_amount) + " " + symbol)
            if call_api() is not None:
                lbl3.config(
                    text="Actual " + currency + " value : " + str(round(cro_amount * call_api(), 2)) + " " + symbol)
        else:
            raise Exception('File structure is not good')


btn = Button(root, text='Choose a CSV file of CRO transactions', command=lambda: open_file())
btn.pack(side=TOP, pady=10, expand=TRUE)

lbl = Label(root, font=18)
lbl.pack(expand=TRUE)

lbl2 = Label(root, font=18)
lbl2.pack(expand=TRUE)

lbl3 = Label(root, font=18)
lbl3.pack(expand=TRUE)

mainloop()
