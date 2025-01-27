class Order(object):
    last_order_number = 0

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

        Order.last_order_number = number
