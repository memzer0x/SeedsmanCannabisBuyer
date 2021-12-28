import requests
from bs4 import BeautifulSoup
import json
import re
from termcolor import colored
import threading
import smtplib, ssl
import optparse

def get_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--url", dest="url", help="URL of the seed at seedsman.org (example : https://www.seedsman.com/us_en/biscotti-mintz-feminised-seeds)")
    parser.add_option("-r", "--recipient", dest="recipient", help="The recipient email to send the mail when the seeds are available. (useful for phone notifications)")
    parser.add_option("-s", "--sender", dest="sender", help="A email account that you will use for sending the mail (REQUIRED), just make a email account with outlook and use their SMTP server")
    parser.add_option("-m", "--smtphost", dest="smtphost", help="A server SMTP that will be used to send the mail (default is smtp-mail.outlook.com:587)")   
    parser.add_option("-p", "--smtpport", dest="smtpport", help="The port of the server SMTP you will use (default is 587)")
    parser.add_option("--password", dest="password", help="The password for the sender email account (REQUIRED)")
    parser.add_option("--seedname", dest="seedname", help="Name of the seed you're going to buy (example : Biscotti Mintz Feminized)")

    (options, arguments) = parser.parse_args()
    if not options.url:
        parser.error("[-] Please specify the url of the seed you want to buy but is currently out of stock, use --help for more informations.")
    if not options.recipient:
        parser.error("[-] Please enter the email address where you wish to receive an email when the seed is available (recipient account)(Highly useful to receive notifications on your phone when ready).")

    return options

def check_seeds(url, recipient, sender, password, seedname, smtphost, smtpport):
    response = requests.get(url)
    res_soup = BeautifulSoup(response.text, "html.parser")
    for i in res_soup.find_all("script"):
        stock_json = re.search(r'\[\{"attribute501":"[0-9]{1,9}","stock":\[\{"store":"[0-9]{1,9}","qty":[0-9]{1,9},"status":"[a-zA-Z0-9_\-]{1,20}","message":"[a-zA-Z0-9_\- ]{1,20}"\}\]\}', i.text)
        if stock_json is not None:
            subset = json.loads(stock_json.group(0) + "]")
            # Make sure we have the right json string
            if subset[0]["attribute501"] != "131":
                print(colored("[-] Failed to obtain strain information !", "red"))
                exit(-1)

            # Check if it's in stock
            if subset[0]["stock"][0]["qty"] != "0" and (subset[0]["stock"][0]["status"] != "out_of_stock" or subset[0]["stock"][0]["message"] != "Out of stock"):
                print(colored("[+] Seeds in stock !", "green"))
                send_mail(url, recipient, sender, password, seedname, smtphost, smtpport)
            else:
                print(colored("[-] Seeds unavailable !", "red"))
                return False

def send_mail(url, recipient, sender, password, seedname, smtphost, smtpport):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    connection = smtplib.SMTP(smtphost, smtpport)
    connection.ehlo()
    connection.starttls(context=context)
    connection.ehlo
    connection.login(sender, password)
    connection.sendmail(sender, recipient, f"""
Sup Sup it's your favorite bot ! Your Seeds of "{seedname}" are finally available.

Go buy them now at the following link : {url}
""")
    connection.close()

    print(colored(f"[+] Seeds are available and an email was sent to {recipient}", "green"))
    exit(1)


def get_seed_name(url):
    # Request the URL parse the title
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    for title in soup.find_all("span"):
        if title.get("class") is not None:
            for tag in title.get("class"):
                if tag == "base":
                    return title.string.rstrip(" ")

def main():
    options = get_arguments()
    SEED_URL = options.url
    MAIL_RECIPIENT = options.recipient
    # MAIL_SENDER
    if options.sender is not None:
        MAIL_SENDER = str(options.sender)
    else:
        MAIL_SENDER = "seeeedsbot@outlook.com"
    # SMTPHOST
    if options.smtphost is not None:
        SMTP_HOST = str(options.smtphost)
    else:
        SMTP_HOST = "smtp-mail.outlook.com"
    # SMTPPORT
    if options.smtpport is not None:
        SMTP_PORT = int(options.smtpport)
    else:
        SMTP_PORT = 587
    # SEEDNAME
    if options.seedname is None:
        SEED_NAME = get_seed_name(SEED_URL)
    else:
        SEED_NAME = options.seedname

    if options.password is not None:
        MAIL_SENDER_PASSWORD = str(options.password)
    else:
        MAIL_SENDER_PASSWORD = "" # If you do not specify a password using commandline you're going to have to hardcode a value in here

    while True:
        check_seeds(SEED_URL, MAIL_RECIPIENT, MAIL_SENDER, MAIL_SENDER_PASSWORD, SEED_NAME, SMTP_HOST, SMTP_PORT)
    # Call check_seeds() with threading on and in an infinite loop until there is some available.
    # When there is some available send an email using outlook smtp servers to i0x60d5@outlook.com
    while True:
        try:
            for i in range(5):
                t = threading.Thread(target=check_seeds)
                t.start()
            
            for i in range(5):
                t.join()
            
            if TO_EXIT == True:
                exit(1)
        except KeyboardInterrupt:
            print(colored("[-] Keyboard Interruption detected, stopping program.", "red"))
            exit(-2)
        except:
            exit(-3)
main()
