import requests
import random
import threading
import time
from faker import Faker
from colorama import Fore, init
from flask import Flask, jsonify

init(autoreset=True)
fake = Faker()
app = Flask(__name__)

PROXY_RETRY_ATTEMPTS = 3
success_count = 0
fail_count = 0
lock = threading.Lock()

def generate_name():
    return fake.name()

def generate_email(name):
    return name.replace(" ", "").lower() + "@gmail.com"

def generate_phone():
    area_codes = ['212', '310', '415', '323', '818', '646', '202', '617', '773', '305']
    return f"+1{random.choice(area_codes)}{random.randint(1000000, 9999999)}"

def get_proxies():
    proxy_sources = [
        "https://api.proxyscrape.com/?request=displayproxies&proxytype=https&timeout=5000",
        "https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=5000",
        "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&timeout=5000"
    ]
    proxies = []
    for url in proxy_sources:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                proxies.extend(response.text.strip().split("\n"))
        except:
            pass
    return proxies if proxies else None

def send_report():
    global success_count, fail_count
    proxies = get_proxies()
    
    if not proxies:
        with lock:
            fail_count += 1
        return
    
    proxy = random.choice(proxies).strip()
    proxies_dict = {'http': proxy, 'https': proxy}

    name = generate_name()
    email = generate_email(name)
    phone = generate_phone()

    url = "https://telegram.org/support"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://telegram.org",
        "Referer": "https://telegram.org/support",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    data = {
        "message": """Dear Telegram Support Team,

I am writing to file a formal complaint against two Telegram channels and a bot, which are engaged in illegal activities and the misuse of personal data. The channels and bot are involved in facilitating scams, illegal BIN and credit card trading, as well as operating a highly risky KYC (Know Your Customer) process that puts users' sensitive information at serious risk.

1. Channel 1: https://t.me/allinworld009
   This channel is involved in the illegal sharing and trading of credit card BINs and other fraudulent activities, violating financial regulations and promoting scams.

2. Group 1 : https://t.me/trustexchangeworld0
   This group facilitates buying and selling transactions, but requires users to go through a KYC process. The KYC process is handled by a bot, @KYC_PRO_BOT, which is owned and operated by the group administrators. The bot asks for sensitive personal information such as pictures and IDs, which are then stored and misused. The data provided is directly sent to the group owner, @Nahidnaim009, who is likely using this information for malicious purposes, such as identity theft or fraudulent activities.

This behavior is illegal and represents a severe breach of privacy and security. It poses a significant risk to users who are unknowingly providing personal information that could be exploited. 

I urgently request that these channels and the bot be investigated and removed from Telegram, and that the responsible individuals involved in these activities be held accountable.

Thank you for your immediate attention to this matter.""",
        "legal_name": name,
        "email": email,
        "phone": phone,
        "setln": ""
    }

    for _ in range(PROXY_RETRY_ATTEMPTS):
        try:
            response = requests.post(url, headers=headers, data=data, proxies=proxies_dict, timeout=10)
            if '<div class="alert alert-success"><b>Thanks for your report&#33;</b>' in response.text:
                with lock:
                    success_count += 1
                print(Fore.GREEN + f"✅ Sent: {success_count} | ❌ Failed: {fail_count} | Credit: @NAR2TO")
            else:
                with lock:
                    fail_count += 1
                print(Fore.RED + f"✅ Sent: {success_count} | ❌ Failed: {fail_count} | Credit: @NAR2TO")
            return
        except:
            pass
    
    with lock:
        fail_count += 1

def start_reporting():
    while True:
        threading.Thread(target=send_report).start()
        time.sleep(0.5)

@app.route('/')
def status():
    return jsonify({
        "success_reports": success_count,
        "failed_reports": fail_count
    })

if __name__ == "__main__":
    threading.Thread(target=start_reporting).start()
    app.run(host="0.0.0.0", port=8080)
