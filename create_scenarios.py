"""
Create a scenario file from the orders that can be executed by the AnyDex simulator.
This script creates a specified number of scenarios by doing a backwards read through the full file.
Every time, it considers X orders.
"""
import os

from file_read_backwards import FileReadBackwards

from order import Order

NUM_ORDERS_IN_BATCH = 10000
NUM_SCENARIOS = 10

cancellations = {}
orders_in_batch = set()
users = set()
current_batch = 1

os.makedirs("scenarios", exist_ok=True)

with FileReadBackwards("orders.txt", encoding="utf-8") as orders_file:
    # We read the orders_file in blocks. For each block height, we sort the orders on timestamp and process them
    # individually afterwards.
    for order_line in orders_file:
        parts = order_line.split(",")
        order = Order.from_line(order_line)
        if order.type == "ask" or order.type == "bid":
            orders_in_batch.add(order)
            users.add(order.user_id)
        elif order.type == "cancel":
            cancellations[order.id] = order

        if len(orders_in_batch) == NUM_ORDERS_IN_BATCH:
            print("Collected %d orders - preparing batch %d" % (NUM_ORDERS_IN_BATCH, current_batch))

            items = []
            min_timestamp = None
            for order in orders_in_batch:
                items.append(order)
                if order.id in cancellations:
                    items.append(cancellations[order.id])
                    del cancellations[order.id]
                if not min_timestamp or order.timestamp < min_timestamp:
                    min_timestamp = order.timestamp

            # Shift tx times
            for item in items:
                item.timestamp -= min_timestamp

            items = sorted(items, key=lambda order: order.timestamp)

            # Write this batch
            with open(os.path.join("scenarios", "%d.txt" % current_batch), "w") as scenario_file:
                for item in items:
                    scenario_file.write(item.to_line())

            orders_in_batch = set()
            current_batch += 1
            if current_batch == NUM_SCENARIOS + 1:
                break


print("Created scenarios!")
