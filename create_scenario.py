"""
Create a scenario file from the orders that can be executed by the AnyDex simulator.
"""
from order import Order

NUM_ORDERS = 10000
users = set()
created_orders = set()
transactions = []
min_timestamp = None

with open("orders.txt", "r") as orders_file:
    # We read the orders_file in blocks. For each block height, we sort the orders on timestamp and process them
    # individually afterwards.
    orders_parsed = 0
    for order_line in orders_file:
        parts = order_line.split(",")
        order = Order.from_line(order_line)
        if order.type == "ask" or order.type == "bid":
            created_orders.add(order.id)

        # We should not have cancellations for orders that we did not create
        if order.type == "cancel" and order.id not in created_orders:
            continue  # Ignore it

        transactions.append(order)
        users.add(order.user_id)
        orders_parsed += 1
        if not min_timestamp or order.timestamp < min_timestamp:
            min_timestamp = order.timestamp

        if orders_parsed == NUM_ORDERS:
            break


# Shift tx times
for transaction in transactions:
    transaction.timestamp -= min_timestamp


with open("scenario.txt", "w") as scenario_file:
    for transaction in transactions:
        scenario_file.write(transaction.to_line())


print("Minimum timestamp: %d" % min_timestamp)
print("Created scenario with %d unique users" % len(users))
