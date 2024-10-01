# Class 'Order' with all orders with the categories of each one (number, reference...)

class Order(object):
    # Class variable to keep track of the last order number
    last_order_number = 0

    # Constructor method to initialize the Order object with provided attributes
    def __init__(self, number, order_line, reference, delivery_date, time_gap,
                 description, model, quantity, color, dimensions):
        self.number = number
        self.order_line = order_line
        self.reference = reference
        self.delivery_date = delivery_date
        self.time_gap = time_gap
        self.description = description
        self.model = model
        self.quantity = int(quantity)
        self.color = color
        self.dimensions = dimensions

        # Update the class variable 'last_order_number' with the current order number
        Order.last_order_number = number
