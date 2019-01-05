import random
import string

class Order:
    def __init__(self, items, dest, due, start):
        
        self.id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.items = items
        self.dest = dest
        self.due = due
        self.start = start
        