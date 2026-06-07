import requests
import time
import os
from datetime import datetime

# CONFIGURATION

TARGET_URL = "https://robotxacademy.site"

CHECK_INTERVAL = 300  # 5 minutes

TIMEOUT_SECONDS = 10

TELEGRAM_BOT_TOKEN = "8356795731:AAF8c-1XZDjo335TfuMKG_tTN1KrlhgGYC8"

TELEGRAM_CHAT_ID = "-5275769272"

STATE_FILE = "state.txt"

HEALTHY_CODES = [200, 202]

# SEND TELEGRAM MESSAGE

def send_telegram(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=data)
        print("Telegram Status:", response.status_code)
        print("Telegram Response:", response.text)

    except Exception as e:
        print("Telegram Error:", e)

# LOAD PREVIOUS STATE

def load_state():

    if not os.path.exists(STATE_FILE):
        return "UP"

    with open(STATE_FILE, "r") as file:
        return file.read().strip()

# SAVE CURRENT STATE

def save_state(state):

    with open(STATE_FILE, "w") as file:
        file.write(state)

# ERROR CLASSIFICATION

def classify_error(status_code):

    if status_code == 400:
        return "Bad Request / Developer Issue"

    elif status_code in [401, 403]:
        return "Authentication or Permission Issue"

    elif status_code == 404:
        return "Page or Route Not Found"

    elif status_code == 500:
        return "Internal Server Error"

    elif status_code == 502:
        return "Bad Gateway / Reverse Proxy Issue"

    elif status_code == 503:
        return "Server Unavailable or Restarting"

    elif status_code == 504:
        return "Gateway Timeout"

    else:
        return "Unknown Server Error"

# MAIN WEBSITE CHECK

def check_website():

    previous_state = load_state()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:

        response = requests.get(
            TARGET_URL,
            timeout=TIMEOUT_SECONDS
        )

        status_code = response.status_code

        print(f"[{current_time}]\nStatus Code:", status_code)

        # WEBSITE IS HEALTHY

        if status_code in HEALTHY_CODES:

            print("Website is UP")

            # RECOVERY DETECTION
            if previous_state == "DOWN":

                message = f"""

✅ RESOLVED: 
{TARGET_URL} 
is Back Online

Status Code : {status_code}

Time : {current_time}

Resolution:
Website recovered successfully.

No further action required.
"""

                send_telegram(message)

            save_state("UP")

        # WEBSITE IS DOWN

        else:

            print("Website is DOWN")

            if previous_state != "DOWN":

                root_cause = classify_error(status_code)

                message = f"""

🚨 ALERT: 
{TARGET_URL} 
is DOWN

Status Code : {status_code}

Time : {current_time}

Root Cause:
{root_cause}

Solutions:
1. Restart web server
2. Check internet/network
3. Verify DNS
4. Contact developer
5. Check hosting provider
"""

                send_telegram(message)

            save_state("DOWN")

    # TIMEOUT / CONNECTION ERROR

    except requests.exceptions.RequestException:

        print("Connection Timeout")

        if previous_state != "DOWN":

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message = f"""

🚨 ALERT: {TARGET_URL} is DOWN

Status Code : TIMEOUT

Time : {current_time}

Root Cause:
Server unreachable or network issue

Solutions:
1. Check hosting status
2. Restart services
3. Check internet connection
4. Verify DNS
"""

            send_telegram(message)

        save_state("DOWN")

# RUN FOREVER

print("Website Monitor Started...")

send_telegram("🤖 Website Monitor Started Successfully")

while True:

    print("\nChecking website...")

    check_website()

    print(f"Waiting {CHECK_INTERVAL} seconds...\n")

    time.sleep(CHECK_INTERVAL)