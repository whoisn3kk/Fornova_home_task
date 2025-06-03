import json
from traceback import format_exc
from playwright.sync_api import sync_playwright

import os
from dotenv import load_dotenv
load_dotenv()

DEEPLINK_URL = os.environ.get("DEEPLINK", "")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

IP = os.environ.get("IP")
PORT = os.environ.get("PORT")
LOGIN = os.environ.get("LOGIN")
PASS = os.environ.get("PASS")

proxies = {
    "http": f"http://{LOGIN}:{PASS}@{IP}:{PORT}",
    "https": f"http://{LOGIN}:{PASS}@{IP}:{PORT}",
}

def main() -> tuple[bool, str]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent=USER_AGENT,
                locale="en-US",
                proxy= {
                    "server": f"http://{IP}:{PORT}",
                    "username": LOGIN,
                    "password": PASS,
                }
            )

            page = context.new_page()
            print(f"Opening deeplink:\n{DEEPLINK_URL}\n")
            page.goto(DEEPLINK_URL, wait_until="networkidle")

            input("Please solve captcha if presented and press ENTER. If capthca is missing, probably all good, just press ENTER.")

            cookies = context.cookies()
            with open("cookies.json", "w", encoding="utf-8") as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            

            print("Cookies saved in cookies.json")
            browser.close()
            return True, "cookies.json"
    except:
        print(format_exc())
        return False, "Check console for additional info!"

if __name__ == "__main__":
    main()
