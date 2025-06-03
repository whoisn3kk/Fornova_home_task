import json
from traceback import format_exc

def extract_rates_from_response(input_file: str="response.json", output_file: str="result.json"):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data:dict = json.load(f)
        
        entries:list[dict] = data.get("data", {}).get("recommendedEntries", [])
        
        lst = []
        for entry in entries:
            rates:list[dict] = entry.get("hotelRoomInventoryList", [])

            for rate in rates:
                
                info = {}
                info["room_name"] = entry.get("name", "")
                info["rate_name"] = rate.get("inventoryName", "")
                info["number_of_guests"] = rate.get("maxOccupancy", "")
                rpc:dict = rate.get("roomCancellationPolicy", {})
                info["cancellation_policy"] = rpc.get("providerCancellationPolicyString", "")
                info["breakfast"] = rate.get("displayNumBreakfastIncluded", "")
                rd:dict = rate.get("rateDisplay", {})
                bf:dict = rd.get("baseFare", {})
                tx:dict = rd.get("taxes", {})
                tf:dict = rd.get("totalFare", {})
                
                info["price"] = bf.get("amount", "")
                info["currency"] = tf.get("currency", "")
                info["total_taxes"] = tx.get("amount", "")
                info["total_price"] = tf.get("amount", "")
        
                ord_rd:dict = rate.get("originalRateDisplay", {})
                if ord_rd and ord_rd.get("totalFare"):
                    info["original_price"] = ord_rd["totalFare"].get("amount", "")
                
                final_price:dict = rate.get("finalPrice", {})
                prpn:dict = final_price.get("perRoomPerNightDisplay", {})
                if prpn:
                    ef:dict = prpn.get("exclusiveFinalPrice", {})
                    inf:dict = prpn.get("inclusiveFinalPrice", {})
                    tfpn:dict = prpn.get("totalFare", {})
                    if ef:
                        info["net_price_per_stay"] = ef.get("amount", "")
                    if inf:
                        info["shown_price_per_stay"] = inf.get("amount", "")
                    if tfpn:
                        info["total_price_per_stay"] = tfpn.get("amount", "")
                
                lst.append(info)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False, indent=2)

        return True, output_file
    except:
        print(format_exc())
        return False, "Error, check console for more information."
    
if __name__ == "__main__":
    input_filename = "response.json"
    output_filename = "result.json"
    
    res, file = extract_rates_from_response(input_filename, output_filename)
    if res:
        print(f"Done! Saved in {file}.")
    else:
        print(file)
