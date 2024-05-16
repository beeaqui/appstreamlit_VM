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
    number = Order.last_order_number  # Use the updated order number
    reference = int("536297")

    product_delivery_date = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(1, 120))
    delivery_date = product_delivery_date.strftime('%H:%M') + ' h'

    current_date = datetime.datetime.now()
    time_gap = product_delivery_date - current_date
    gap = time_gap

    total_seconds = gap.total_seconds()

    # Convert seconds to hours, minutes, and seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    # seconds = int(total_seconds % 60)

    # Format the time_gap as "hours:minutes:seconds"
    time_gap = f"{hours:02d}:{minutes:02d} h"

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
        collection14 = db['PreSelectedOrders']
        collection15 = db['ValueGenerateOrders']
        collection16 = db['HighPriority']

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
        collection14.drop()

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
            cursor = collection15.find()
            time_interval = 1
            for document in cursor:
                value = int(document['Time Interval Generate Order'])
                time_interval = int(value)

            sleep(random.randint(1, time_interval))
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
    Order.last_order_number = 0
    thread_create_orders.start()
