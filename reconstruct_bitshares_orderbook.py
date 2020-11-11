"""
This script extracts all orders from the Bitshares blockchain and writes them to a file.

We write everything away to orders.txt, which contains the following columns:
- height: the height of the operation (order/cancel) in the blockchain
- id: an identifier of the order, in bitshares the operation ID (e.g. 1.7.12345)
- type: type of the order: ask, bid or cancel
- asset1_amount: amount of the first asset
- asset1_type: type of the first asset
- asset2_amount: amount of the second asset
- asset2_type: type of the second asset
- user_id: identifier of the user, in bitshares the account ID (e.g. 1.2.12345)
- timeout: the timeout of the order in milliseconds from epoch
- timestamp: the timestamp of the order in milliseconds from epoch
"""
import os
import random
import subprocess
import time
from datetime import datetime

from grapheneapi.grapheneapi import GrapheneAPI
from grapheneapi.exceptions import RPCConnection

from order import Order

rpc = GrapheneAPI("127.0.0.1", 8090)


def get_block(height):
    global rpc
    block = None
    while not block:
        try:
            block = rpc.get_block(height)
        except RPCConnection:
            print("Connection failed - waiting 10 sec and retry again")
            time.sleep(10)
    return block


def process_block(block, height, prev_block=None):
    block_time_date = datetime.strptime(block["timestamp"], '%Y-%m-%dT%H:%M:%S')
    block_time = (block_time_date - datetime(1970, 1, 1)).total_seconds() * 1000

    if not prev_block:
        if height > 1:
            prev_block = get_block(height - 1)

    if prev_block:
        prev_block_time_date = datetime.strptime(prev_block["timestamp"], '%Y-%m-%dT%H:%M:%S')
        prev_block_time = (prev_block_time_date - datetime(1970, 1, 1)).total_seconds() * 1000
    else:
        prev_block_time = block_time

    orders = []

    for transaction in block["transactions"]:
        num_ops = len(transaction["operation_results"])
        for op_ind in range(num_ops):
            op_type = transaction["operations"][op_ind][0]
            if op_type == 1:  # Create limit order
                op_id = transaction["operation_results"][op_ind][1]
                op_dict = transaction["operations"][op_ind][1]

                user_id = op_dict["seller"]
                sell_asset_id = op_dict["amount_to_sell"]["asset_id"]
                sell_amount = int(op_dict["amount_to_sell"]["amount"])
                receive_asset_id = op_dict["min_to_receive"]["asset_id"]
                receive_amount = int(op_dict["min_to_receive"]["amount"])
                exp_time_date = datetime.strptime(op_dict["expiration"], '%Y-%m-%dT%H:%M:%S')
                exp_time = (exp_time_date - datetime(1970, 1, 1)).total_seconds() * 1000

                if exp_time <= block_time:
                    continue

                timeout = exp_time - block_time

                if sell_asset_id < receive_asset_id:
                    asset1_type = sell_asset_id
                    asset1_amount = sell_amount
                    asset2_type = receive_asset_id
                    asset2_amount = receive_amount
                    order_type = "ask"
                else:
                    asset1_type = receive_asset_id
                    asset1_amount = receive_amount
                    asset2_type = sell_asset_id
                    asset2_amount = sell_amount
                    order_type = "bid"

                create_timestamp = random.randint(prev_block_time, block_time)

                # Create and append the order
                order = Order(height, op_id, order_type, asset1_amount, asset1_type, asset2_amount, asset2_type, user_id, timeout, create_timestamp)
                orders.append(order)
            elif op_type == 2:  # Create cancel order
                op_dict = transaction["operations"][op_ind][1]

                user_id = op_dict["fee_paying_account"]
                order_id = op_dict["order"]
                order_type = "cancel"
                cancel_timestamp = random.randint(prev_block_time, block_time)

                # Write away the cancel order
                order = Order(height, order_id, order_type, 0, '', 0, '', user_id, 0, cancel_timestamp)
                orders.append(order)

    # Write away all the orders
    with open("orders.txt", "a") as orders_file:
        for order in orders:
            orders_file.write(order.to_line())


# Read parsed orders
parsed_orders = []
cur_height = 2

if os.path.exists("orders.txt"):
    print("File already exists!")
    line = subprocess.check_output(['tail', '-1', "orders.txt"])
    last_order = Order.from_line(line.decode())
    cur_height = last_order.height + 1

print("Starting at height: %d" % cur_height)

prev_block = None
block = get_block(cur_height)
while block:
    try:
        process_block(block, cur_height, prev_block=prev_block)
    except Exception as exc:
        print("Failed to parse block %d!" % cur_height)
        print(exc)
        exit(1)

    prev_block = block
    cur_height += 1
    if cur_height % 1000 == 0:
        print("At block height %d" % cur_height)
    block = get_block(cur_height)
