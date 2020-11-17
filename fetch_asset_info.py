"""
Fetch asset info (precision + price) from Cryptofresh.
"""
from time import sleep

import requests

with open("asset_prices.txt", "w") as assets_price_file:
    with open("missing_assets.txt", "r") as missing_assets_file:
        for line in missing_assets_file.readlines():
            missing_asset_id = line.strip()
            print("Requesting info on asset %s" % missing_asset_id)
            response = requests.get("http://cryptofresh.com/api/asset/markets?asset=%s" % missing_asset_id)
            json_data = response.json()
            if 'BTS' not in json_data:
                print("BTS pricing info not available for %s!" % missing_asset_id)
                continue
            price = json_data["BTS"]["price"]
            assets_price_file.write("%s,%f\n" % (missing_asset_id, price))

            sleep(1)
