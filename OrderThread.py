# Imports
from datetime import datetime
import datetime
import random
from time import sleep
import threading
import csv
from pymongo import MongoClient
from Order import *

keep_on_going_event = threading.Event()


def update_delivery_date():
    try:
        # Read the CSV file into memory
        with open('../appstreamlit_VM/client_orders.csv', 'r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)  # Read all rows into a list
    except Exception as e:
        print("Error:", e)
        return  # Exit the function if there's an error opening the file

    updated_rows = []
    for row in rows:
        # Generate random delivery date within the next 120 minutes
        product_delivery_date = datetime.datetime.now() + datetime.timedelta(minutes=random.randint(1, 30))
        delivery_date = product_delivery_date.strftime('%H:%M') + ' h'

        # Calculate time gap between current time and delivery date
        current_date = datetime.datetime.now()
        time_gap = product_delivery_date - current_date
        total_seconds = time_gap.total_seconds()

        # Convert seconds to hours and minutes
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        # Format the time gap as "hours:minutes h"
        time_gap_formatted = f"{hours:02d}:{minutes:02d} h"

        # Update the delivery_date and time_gap fields in the row
        row['delivery_date'] = delivery_date
        row['time_gap'] = time_gap_formatted

        # Append the updated row to the list
        updated_rows.append(row)

    # Write the updated data back to the CSV file
    with open('../appstreamlit_VM/client_orders.csv', 'w', newline='') as file:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()
        # Write the updated rows
        writer.writerows(updated_rows)


def read_orders_from_csv():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['local']
    collection18 = db['GamePhaseConfig']
    cursor = collection18.find()

    orders = []
    for document in cursor:
        if document['Game Phase'] == "Game 1":
            with open('../appstreamlit_VM/client_orders.csv', mode='r') as file:
                csv_reader = csv.DictReader(file)

                for row in csv_reader:
                    orders.append(Order(
                        str(row['number']),
                        row['order_line'],
                        int(row['reference']),
                        row['delivery_date'],
                        row['time_gap'],
                        row['description'],
                        row['model'],
                        int(row['quantity']),
                        row['color'],
                        row['dimensions']
                    ))
                if not orders:
                    return None

        elif document['Game Phase'] == "Game 2":
            with open('../appstreamlit_VM/client_orders.csv', mode='r') as file:
                csv_reader = csv.DictReader(file)

                for row in csv_reader:
                    i = 0
                    for i in range(int(row['quantity'])):
                        picker = str(i + 1)
                        orders.append(Order(
                            str(picker + '/' + row['quantity']),
                            row['order_line'],
                            int(row['reference']),
                            row['delivery_date'],
                            row['time_gap'],
                            row['description'],
                            row['model'],
                            int(1),  # quantity
                            row['color'],
                            row['dimensions']
                        ))

        else:
            return None

        return orders


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
        collection17 = db['MediumPriority']
        collection18 = db['GamePhaseConfig']
        collection19 = db['LogisticsOrders']
        collection20 = db['LogisticsOrdersProcess']
        collection21 = db['AssemblyOrders']
        collection22 = db['AssemblyOrdersProcess']

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
        collection19.drop()
        collection20.drop()
        collection21.drop()
        collection22.drop()

        update_delivery_date()
        order = read_orders_from_csv()
        row_count = 0

        if order is None:
            return

        while not keep_on_going_event.is_set():

            if row_count >= len(order)-1:
                semaphore()

            aux_count = row_count
            addition = 1

            for aux_count in range(aux_count, len(order)):
                collection.insert_one(
                    {'number': order[aux_count].number, 'order_line': order[aux_count].order_line,
                     'reference': order[aux_count].reference,
                     'delivery_date': order[aux_count].delivery_date,
                     'time_gap': order[aux_count].time_gap, 'description': order[aux_count].description,
                     'model': order[aux_count].model,
                     'quantity': order[aux_count].quantity, 'color': order[aux_count].color,
                     'dimensions': order[aux_count].dimensions})

                cust_order_datetime = datetime.datetime.now()
                date_cust_order = cust_order_datetime.date().strftime('%Y-%m-%d')
                time_cust_order = cust_order_datetime.time().strftime('%H:%M:%S')

                collection8.insert_one({
                    'Order Number': order[aux_count].number,
                    'Generated Cust_Order': {
                        'Date': date_cust_order,
                        'Time': time_cust_order
                    }
                })

                print("Generated new Order with Id - ", i)

                if aux_count + 1 > len(order)-1:
                    semaphore()
                if order[aux_count].reference != order[aux_count + 1].reference:
                    break

                addition += 1

            i += 1
            row_count += addition

            cursor = collection15.find()
            time_interval = 1
            for document in cursor:
                value = int(document['Time Interval Generate Order'])
                time_interval = int(value)

            sleep(random.randint(1, time_interval))
        keep_on_going = True

    except:
        print("Exception: out of thread.")


def semaphore():
    print("Semaphore called.")
    keep_on_going_event.set()
    print("Thread stopped.")


def start_thread():
    print("Starting thread...")
    keep_on_going_event.clear()
    thread_create_orders = threading.Thread(target=run)
    Order.last_order_number = 0
    thread_create_orders.start()
