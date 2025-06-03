import json
from traceback import format_exc

def extract_rates_from_response(room_to_find: str, input_file: str="response.json", output_file: str="result.json"):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data.get("data", {}).get("recommendedEntries", [])
        
        target_entry = None
        for entry in entries:
            if entry.get("name") == room_to_find:
                target_entry = entry
                break
        
        if not target_entry:
            if not entries:
                result = { "error": f"{room_to_find} room missing in response json" }
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                return True, output_file 
            target_entry = entries[0]
        
        rates = target_entry.get("hotelRoomInventoryList", [])
        if not rates:
            result = { "error": f"{room_to_find} rates missing in response json" }
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            return True, output_file
        
        inv = rates[0]
        
        info = {}
        info["room_name"] = target_entry.get("name", "")
        info["rate_name"] = inv.get("roomInventoryGroupOption", "")
        info["number_of_guests"] = inv.get("maxOccupancy", "")
        rpc = inv.get("roomCancellationPolicy", {})
        info["cancellation_policy"] = rpc.get("providerCancellationPolicyString", "")
        info["breakfast"] = inv.get("displayNumBreakfastIncluded", "")
        rd = inv.get("rateDisplay", {})
        bf = rd.get("baseFare", {})
        tx = rd.get("taxes", {})
        tf = rd.get("totalFare", {})
        
        info["price"] = tf.get("amount", "")
        info["currency"] = tf.get("currency", "")
        info["total_taxes"] = tx.get("amount", "")
        info["total_price"] = tf.get("amount", "")
        
        ord_rd = inv.get("originalRateDisplay", {})
        if ord_rd and ord_rd.get("totalFare"):
            info["original_price"] = ord_rd["totalFare"].get("amount", "")
        
        final_price = inv.get("finalPrice", {})
        prpn = final_price.get("perRoomPerNightDisplay", {})
        if prpn:
            ef = prpn.get("exclusiveFinalPrice", {})
            inf = prpn.get("inclusiveFinalPrice", {})
            tfpn = prpn.get("totalFare", {})
            if ef:
                info["net_price_per_stay"] = ef.get("amount", "")
            if inf:
                info["shown_price_per_stay"] = inf.get("amount", "")
            if tfpn:
                info["total_price_per_stay"] = tfpn.get("amount", "")
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)

        return True, output_file
    except:
        print(format_exc())
        return False, "Error, check console for more information."
    
if __name__ == "__main__":
    input_filename = "response.json"
    output_filename = "result.json"
    room_name = "Superior Twin With Ocean View"
    
    res, file = extract_rates_from_response(input_filename, room_name, output_filename)
    if res:
        print(f"Done! Saved in {file}.")
    else:
        print(file)
