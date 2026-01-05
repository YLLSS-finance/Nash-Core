# Order Format
# Index | Content 
# 0 | Order ID
# 1 | Timestamp
# 2 | Market Participant ID
# 3 | Contract ID
# 4 | Limit Price
# 5 | Order Side
# 6 | Order Quantity [red, inc]
# 7 | Order Head/Tail [head, tail]

from sortedcontainers import SortedDict

# TODO: Add method for checking and ensuring order integrity

class MarginManager:
    def __init__(self, _account, market_id):
        self.order_book = _account._master.order_books
        self.marketID = market_id

        # Pointers to things in the account which the margin manager serves
        self.balance = _account.margin
        self.orders = _account.orders
        self.position = _account.positions[market_id]
        
        if not market_id in _account.positions:
            _account.positions[market_id] = [0, 0]
        
        # Determine reducible component 
        self.reducible = self.position[:]
        for order in self.orders.values():
            if order[3] == self.marketID:
                self.reducible[1 - order[5]] -= order[6][0]

        self.levels = [SortedDict(key=lambda x:-x), SortedDict(key=lambda x:x)]
        self.redOnlyLevels = [0, 0]
        self.redOnlyPrices = [None, None]
        
    def add_order(self, order):
        '''
        Logs an order's quantities into the levels sorteddict and updates related caches.
        '''
        # Extract the properties of the order
        order_side = order[5]
        order_price = order[4]
        order_red, order_inc = order[6]
        
        side_level = self.levels[order_side]
        
        # Reminder: Reduce-Only level amount can only be increased by a new level!
        # This is because adding orders to an level may only cause a Reduce-Only Level to lose such status as the order contains an increase quantity
        # and additions of Reduce-Only Orders into a Reduce-Only level would only maintain its status.
        
        if not order_price in side_level:
            side_level[order_price] = order[6][:]

            if order_red and (not order_inc):
                # If the incoming order creates the FIRST reduce-only level in the side of the order, set the reduce-only price accordingly
                if not self.redOnlyLevels[order_side]:
                    self.redOnlyPrices[order_side] = order_price
                self.redOnlyLevels[order_side] += 1 
            return
        
        level_qtys = side_level[order_price]
        prev_red, prev_inc = level_qtys
        prev_red_only = prev_red and (not prev_inc)
        
        if prev_red_only and order_inc: 
            # If the incoming order removes the ONLY reduce-only level in the side of the order, clear the reduce-only price on that side
            self.redOnlyLevels[order_side] -= 1
            if not self.redOnlyLevels[order_side]:
                self.redOnlyPrices[order_side] = None
                
        # Finally, update the quantities at that level
        level_qtys[0] += order_red
        level_qtys[1] += order_inc
    
    def accept_order(self, price, side, qty):
        red = min(qty, self.reducible[1 - side])
        inc = qty - red
        
        