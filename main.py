from utils.get_session import main as get_session
from utils.get_rooms import main as get_rooms

from utils.response_parse import extract_rates_from_response

def main():
    success, msg = get_rooms()
    if not success:
        print(msg)
        session_res, msg = get_session()
        if not session_res:
            print(msg)
            return
        success, msg = get_rooms()
        if not success:
            print("Something went wrong")
            print(msg)
            return
        
    res, file = extract_rates_from_response()
    if res:
        print(f"Done! Saved in {file}.")
    else:
        print(file)

if __name__ == "__main__":
    main()