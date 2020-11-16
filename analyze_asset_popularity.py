"""
Go through all orders and determine the popularity of specific assets.
"""
from order import Order

assets_frequency = {}

with open("orders.txt", "r") as orders_file:
    # We read the orders_file in blocks. For each block height, we sort the orders on timestamp and process them
    # individually afterwards.
    orders_parsed = 0
    for order_line in orders_file:
        parts = order_line.split(",")
        order = Order.from_line(order_line)
        if order.type == "ask" or order.type == "bid":
            if order.asset1_type not in assets_frequency:
                assets_frequency[order.asset1_type] = 0
            assets_frequency[order.asset1_type] += 1

            if order.asset2_type not in assets_frequency:
                assets_frequency[order.asset2_type] = 0
            assets_frequency[order.asset2_type] += 1

        orders_parsed += 1

        if orders_parsed % 1000000 == 0:
            print("Parsed %d orders!" % orders_parsed)


assets = []
for asset_type, asset_frequency in assets_frequency.items():
    assets.append((asset_type, asset_frequency))
assets = sorted(assets, key=lambda tup: tup[1], reverse=True)

with open("assets_info.csv", "w") as assets_file:
    assets_file.write("asset_id,orders\n")
    for asset_type, asset_frequency in assets:
        assets_file.write("%s,%d\n" % (asset_type, asset_frequency))
        print("Asset %s in %d orders!" % (asset_type, asset_frequency))
