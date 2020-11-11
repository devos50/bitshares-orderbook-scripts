"""
Find the window in which the most number of orders has been made
"""
from order import Order

WINDOW = 300

best_start_time = 0
best_num_orders = 0
best_orders = []

orders_parsed = 0
cur_time = 0
cur_orders = []
cur_num_orders = 0
processed = 0

cur_block_height = 0
to_process = []


def process_batch():
    global to_process

    # Sort the orders based on timestamp
    to_process.sort(key=lambda order: order.timestamp)

    for order in to_process:
        process_order(order)
    to_process = []


def process_order(order):
    global processed, cur_time, cur_num_orders, cur_orders, best_num_orders, best_start_time, best_orders
    processed += 1

    if processed % 1000000 == 0:
        print("Processed %d lines..." % processed)

    order_time = int(parts[9])
    order_type = parts[2]

    if cur_time == 0:  # Initialize the stuff
        cur_time = order_time
        if order_type == "ask" or order_type == "bid":
            cur_orders = [order_line]
            cur_num_orders += 1
        return

    if order_type == "cancel":
        if order_time <= cur_time + WINDOW * 1000:
            # Still include it
            cur_orders.append(order_line)
            return

    if order_time > cur_time + WINDOW * 1000:
        # Stop this segment and start a new one
        if cur_num_orders > best_num_orders:
            best_start_time = cur_time
            best_num_orders = cur_num_orders
            best_orders = cur_orders

            print("Found new best: time: %d, %d orders within %d seconds" % (cur_time, best_num_orders, WINDOW))

            # Write away!
            with open("orders_interval.txt", "w") as output_file:
                for order in cur_orders:
                    output_file.write(order)

        cur_time = order_time
        cur_orders = [order_line]
        cur_num_orders = 0
    elif order_type == "ask" or order_type == "bid":
        cur_orders.append(order_line)
        cur_num_orders += 1


with open("orders.txt", "r") as orders_file:
    # We read the orders_file in blocks. For each block height, we sort the orders on timestamp and process them
    # individually afterwards.
    for order_line in orders_file:
        parts = order_line.split(",")
        order = Order.from_line(order_line)
        if not order:
            continue

        if order.height != cur_block_height:
            process_batch()
            to_process.append(order)
