import json
import uuid
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime

import os
from dotenv import load_dotenv
load_dotenv()
IP = os.environ.get("IP")
PORT = os.environ.get("PORT")
LOGIN = os.environ.get("LOGIN")
PASS = os.environ.get("PASS")

DEEPLINK_URL = os.environ.get("DEEPLINK", "")

ROOMS_URL = os.environ.get("ROOMS_URL", "")

PROXY_URL = f"http://{LOGIN}:{PASS}@{IP}:{PORT}"


def parse_spec_from_deeplink(deeplink: str) -> dict:
    parsed = urlparse(deeplink)
    qs = parse_qs(parsed.query)
    spec_list = qs.get("spec")
    if not spec_list:
        raise RuntimeError("spec missing in DEEPLINK_URL")
    spec = spec_list[0]  # "03-06-2025.04-06-2025.1.1.HOTEL.9000001153383.Name.2"
    parts = spec.split(".")

    # parts[0] = 03-06-2025 # from
    # parts[1] = 04-06-2025 # to
    # parts[2] = 1 
    # parts[3] = 2 # numRooms
    # parts[4] = HOTEL 
    # parts[5] = 9000001153383 # hotelId 
    # parts[6] = Radisson Resort & Spa HuaHin # hotelName
    # parts[7] = 2 # numAdults

    def parse_date_str(date_str: str):
        day_str, month_str, year_str = date_str.split("-")
        return {
            "day": day_str.lstrip("0") or "0",
            "month": month_str.lstrip("0") or "0",
            "year": year_str
        }

    checkin = parse_date_str(parts[0])
    checkout = parse_date_str(parts[1])

    fmt = "%d-%m-%Y"
    d1 = datetime.strptime(parts[0], fmt)
    d2 = datetime.strptime(parts[1], fmt)
    num_nights = (d2 - d1).days

    hotel_id = parts[5]

    num_adults = parts[7]
    num_rooms = parts[3]

    hotel_name = parts[6]

    return {
        "checkInDate": checkin,
        "checkOutDate": checkout,
        "numOfNights": num_nights,
        "hotelId": hotel_id,
        "numRooms": num_rooms,
        "numAdults": num_adults,
        "hotelName": hotel_name
    }

def build_payload(deeplink: str) -> dict:
    parsed_data = parse_spec_from_deeplink(deeplink)
    hotel_detail_url = deeplink

    payload = {
        "fields": [],
        "data": {
            "contexts": {
                "hotelDetailURL": hotel_detail_url,
                "bookingId": None,
                "sourceIdentifier": "HOTEL_DETAIL",
                "shouldDisplayAllRooms": True
            },
            "prevSearchId": "undefined",
            "numInfants": 0,
            "ccGuaranteeOptions": {
                "ccInfoPreferences": ["CC_TOKEN", "CC_FULL_INFO"],
                "ccGuaranteeRequirementOptions": ["CC_GUARANTEE"]
            },
            "rateTypes": ["PAY_NOW", "PAY_AT_PROPERTY"],
            "isJustLogin": False,
            "isReschedule": False,
            "preview": False,
            "monitoringSpec": {
                "referrer": hotel_detail_url,
                "lastKeyword": parsed_data["hotelName"], 
                "isPriceFinderActive": "null",
                "dateIndicator": "null",
                "displayPrice": "null"
            },
            "hotelId": parsed_data["hotelId"],
            "currency": "THB",
            "labelContext": {},
            "isExtraBedIncluded": True,
            "hasPromoLabel": False,
            "supportedRoomHighlightTypes": ["ROOM"],
            "checkInDate": {
                "day": parsed_data["checkInDate"]["day"],
                "month": parsed_data["checkInDate"]["month"],
                "year": parsed_data["checkInDate"]["year"]
            },
            "checkOutDate": {
                "day": parsed_data["checkOutDate"]["day"],
                "month": parsed_data["checkOutDate"]["month"],
                "year": parsed_data["checkOutDate"]["year"]
            },
            "numOfNights": parsed_data["numOfNights"],
            "numAdults": parsed_data["numAdults"],
            "numRooms": parsed_data["numRooms"],
            "numChildren": 0,
            "childAges": [],
            "tid": str(uuid.uuid4)
        },
        "clientInterface": "desktop"
    }
    return payload

def main() -> tuple[bool, str]:
    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL,
    }

    if not os.path.exists("cookies.json"):
        print("Cookies file missing!")
        return False, "Cookies file missing!"
    
    with open("cookies.json", "r", encoding="utf-8") as f:
        try:
            cookies = json.load(f)
        except:
            print("Cant parse cookies, invalid json.")
            return False, "Cant parse cookies, invalid json."
        
    cookies_lst = {i.get("name"): i.get("value") for i in cookies}

    if not os.path.exists("headers.json"):
        print("Headers file missing!")
        return False, "Headers file missing!"
    
    with open("headers.json", "r", encoding="utf-8") as f:
        try:
            browser_headers = json.load(f)
        except:
            print("Cant parse headers, invalid json.")
            return False, "Cant parse headers, invalid json."
        browser_headers["referer"] = DEEPLINK_URL

    payload = build_payload(DEEPLINK_URL)
    resp = requests.post(ROOMS_URL, headers=browser_headers, proxies=proxies, cookies=cookies_lst, data=json.dumps(payload))

    # print(json.dumps(payload, indent=2))

    print(resp.status_code)
    with open("get_rooms.html", "w", encoding="utf-8") as file:
        file.write(resp.text)

    try:
        with open("response.json", "w", encoding="utf-8") as f:
            json.dump(resp.json(), f, ensure_ascii=False, indent=2)
        return True, "response.json"
    except:
        print("Can't parse json from response, check get_rooms.html!")
        return False, "Can't parse json from response, check get_rooms.html!"

if __name__ == "__main__":
    main()