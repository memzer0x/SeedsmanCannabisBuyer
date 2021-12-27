import requests
from bs4 import BeautifulSoup
import json
import re
from termcolor import colored
import threading
import smtplib, ssl

SEED_URL = "https://www.seedsman.com/us_en/biscotti-mintz-feminised-seeds"
MAIL_RECIPIENT = "mail_recipient@outlook.com"
MAIL_SENDER = "seeeedsbot@outlook.com"
MAIL_SENDER_PASSWORD = ""
SMTP_PORT = 587
SMTP_HOST = "smtp-mail.outlook.com"

SUCCESSFUL_MAIL_MESSAGE = """
Sup Sup it's your favorite bot ! Your Seeds of "Biscotti Mintz" are finally available.

Go buy them now at the following link : https://www.seedsman.com/us_en/biscotti-mintz-feminised-seeds
"""

def check_seeds():
    response = requests.get(SEED_URL)
    res_soup = BeautifulSoup(response.text, "html.parser")
    for i in res_soup.find_all("script"):
        stock_json = re.search(r'\[\{"attribute501":"[0-9]{1,9}","stock":\[\{"store":"[0-9]{1,9}","qty":[0-9]{1,9},"status":"out_of_stock","message":"Out of stock"\}\]\}', i.text)
        if stock_json is not None:
            subset = json.loads(stock_json.group(0) + "]")
            # Make sure we have the right json string
            if subset[0]["attribute501"] != "131":
                print(colored("[-] Failed to obtain strain information !", "red"))
                exit(-1)

            # Check if it's in stock
            if subset[0]["stock"][0]["qty"] != "0" and (subset[0]["stock"][0]["status"] != "out_of_stock" or subset[0]["stock"][0]["message"] != "Out of stock"):
                print(colored("[+] Seeds in stock !", "green"))
                send_mail()
            else:
                print(colored("[-] Seeds unavailable !", "red"))
                return False

def send_mail():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    connection = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    connection.ehlo()
    connection.starttls(context=context)
    connection.ehlo
    connection.login(MAIL_SENDER, MAIL_SENDER_PASSWORD)
    connection.sendmail(MAIL_SENDER, MAIL_RECIPIENT, SUCCESSFUL_MAIL_MESSAGE)
    connection.close()

    print(colored(f"[+] Seeds are available and an email was sent to {MAIL_RECIPIENT}", "green"))
    exit(1)

def main():
    # Call check_seeds() with threading on and in an infinite loop until there is some available.
    # When there is some available send an email using outlook smtp servers to i0x60d5@outlook.com
    while True:
        try:
            for i in range(30):
                t = threading.Thread(target=check_seeds)
                t.start()
        except KeyboardInterrupt:
            print(colored("[-] Keyboard Interruption detected, stopping program.", "red"))
            exit(-2)
        except:
            exit(-3)
main()
