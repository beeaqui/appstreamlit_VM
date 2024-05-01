# Imports
from datetime import datetime
import datetime
import random
from time import sleep
import threading
from pymongo import MongoClient
from Order import *


# Lists of product descriptions, models, and colors
product_descriptions = ["Pneumatic Cylinder ADN-40-60-A-P-A"]
product_models = ["Standard", "Sensor Kit"]
product_colors = ['Grey Metal']

keep_on_going_event = threading.Event()


# Function to generate a random order
def generate_random_order():
    Order.last_order_number += 1  # Increment the class attribute for the new order
    product_delivery_date = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(1, 120))

    current_date = datetime.datetime.now()
    time_gap = product_delivery_date - current_date
    gap = time_gap

    number = Order.last_order_number  # Use the updated order number
    reference = int("536297")
    delivery_date = product_delivery_date.strftime('%H:%M') + 'h'
    time_gap = str(gap) + 'h'
    description = random.choice(product_descriptions)
    model = random.choice(product_models)
    quantity = random.randint(1, 12)
    color = random.choice(product_colors)
    dimensions = f"13.01 x 5.45 x 5.45 cm"

    return Order(number, reference, delivery_date, time_gap, description, model, quantity, color, dimensions)


# Main function to run the program
def run():
    try:
        # Connect to the MongoDB database
        client = MongoClient("mongodb://localhost:27017/")
        db = client['local']
        collection = db['ordersCollection']
        collection2 = db['selectedOrders']
        collection3 = db['qualityOrders']
        collection4 = db['qualityApproved']
        collection5 = db['qualityDisapproved']
        collection6 = db['expeditionOrders']
        collection7 = db['ordersConcluded']
        collection8 = db['GenerateOrderTime']
        collection9 = db['TimeOrderReleased']
        collection10 = db['TimeProductionFinished']
        collection11 = db['TimeExpeditionEnd']
        collection12 = db['LeadTimeOrders']
        collection13 = db['CumulativeOrdersFinished']

        print("Connected successfully")
        i = 0

        collection.drop()
        collection2.drop()
        collection3.drop()
        collection4.drop()
        collection5.drop()
        collection6.drop()
        collection7.drop()
        collection8.drop()
        collection9.drop()
        collection10.drop()
        collection11.drop()
        collection12.drop()
        collection13.drop()

        while not keep_on_going_event.is_set():
            order = generate_random_order()

            collection.insert_one(
                {'number': order.number, 'reference': order.reference, 'delivery_date': order.delivery_date,
                 'time_gap': order.time_gap, 'description': order.description, 'model': order.model,
                 'quantity': order.quantity, 'color': order.color, 'dimensions': order.dimensions})

            cust_order_datetime = datetime.datetime.now()
            date_cust_order = cust_order_datetime.date().strftime('%Y-%m-%d')
            time_cust_order = cust_order_datetime.time().strftime('%H:%M:%S')

            collection8.insert_one({
                'Order Number': order.number,
                'Generated Cust_Order': {
                    'Date': date_cust_order,
                    'Time': time_cust_order
                }
            })

            print("Generated new Order with Id - ", i)

            i += 1
            sleep(random.randint(1, 30))
        keep_on_going = True

    except:
        print("Could not connect to MongoDB")
    print("Thread stopped.")


def semaphore():
    print("Semaphore called.")
    keep_on_going_event.set()


def start_thread():
    print("Starting thread...")
    keep_on_going_event.clear()
    thread_create_orders = threading.Thread(target=run)
    thread_create_orders.start()
