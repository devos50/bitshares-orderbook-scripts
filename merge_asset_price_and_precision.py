"""
Merge the fetched asset prices and precisions
"""

precisions = {}
prices = {}
with open("asset_precisions.txt") as precision_file:
    for line in precision_file.readlines():
        parts = line.strip().split(",")
        precisions[parts[0]] = int(parts[1])

with open("asset_prices.txt") as prices_file:
    for line in prices_file.readlines():
        parts = line.strip().split(",")
        prices[parts[0]] = float(parts[1])


for asset_id in prices:
    if asset_id not in precisions:
        continue

    print("    \"%s\": (%d, %f * BTS_USD)," % (asset_id, precisions[asset_id], prices[asset_id]))
