# FORNOVA HOME TASK (Traveloka)

> Required: Python 3.7+

> Tested on: Python 3.11.4

> Proxy: HTTP Russia Moskva, Moscow

_all test data placed in demo/ folder, move it into root folder for testing_

## How to use:

1. Install dependencies:

`pip install -r requirements.txt`

`playwright install`

2. Modify **.env** according to your needs. _Please make sure you set correct proxy credentials and correct Traveloka deeplink_
3. Run `python main.py`
4. If session dead or `cookies.json` missing, you will be asked to manualy confirm session. Solve the captcha if it exist, and press ENTER. _(due poor proxy, it was only way to bypass the captcha.)_
5. Result will be saved in `result.json`

