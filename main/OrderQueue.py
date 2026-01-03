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

class orderQueue:
    def __init__(self, side, fill_order, remove_order):
        self.side = side
        self.levels = SortedDict(key=lambda x:-x) if side == 0 else SortedDict()
        self.topOfBook = None
        self.fill_order = fill_order
        self.cancel_order = remove_order
    
    @property
    def bestPriceQty(self):
        if self.levels:
            price, lvlInfo = self.levels.peekitem(0)
            return [price, lvlInfo[2]]
        return
    
    def fill_top(self, price, qty):
        filled_qty = 0        
        while True:
            if not self.topOfBook: break
            if not qty: break
            
            best_price = self.topOfBook[0]
            if self.side == 0:
                if price > best_price: break
            else:
                if price < best_price: break
                
            best_order = self.levels[best_price]
            fill_qty = min(qty, sum(best_order[6]))
            self.fill_order(best_order, best_price, fill_qty)
            qty -= fill_qty
            filled_qty += fill_qty
        
        return best_price, filled_qty
        
    def initialize(self, orders):
        orders_dict = {}
        for order in orders:
            if not order[4] in orders_dict:
                orders_dict[order[4]] = []
            orders_dict[order[4]].append(order)

        # Sort all orders in each price level by price-time priority
        for order_list in orders_dict:
            order_list.sort(key=lambda x:x[1])

        self.levels.clear()
        self.topOfBook = None
        for price_level, orders_at_level in orders_dict.items():
            total_qty = sum([sum(order[6]) for order in orders_at_level])
            total_orders = len(orders_at_level)
            self.levels[price_level] = [orders_at_level[0], orders_at_level[-1], total_qty, total_orders]

        self.topOfBook = self.bestPriceQty
    
    def post_order(self, order):
        order_price = order[4]
        order_qty = sum(order[6])
        if not order_price in self.levels:
            self.levels[order_price] = [order, order, order_qty, 1]
            if self.topOfBook is None:
                self.topOfBook = self.bestPriceQty
                return
            
            if self.side == 0:
                if order_price > self.topOfBook[0]: self.topOfBook = self.bestPriceQty
            else:
                if order_price < self.topOfBook[0]: self.topOfBook = self.bestPriceQty
            return
        
        level = self.levels[order_price]
        level_tail = level[1]
        level_tail[7][1] = order
        order[7] = [level_tail, None]
        level[1] = order
        level[2] += order_qty
        level[3] += 1
    
    def purge_order(self, order):
        """
        Removes an order from the doubly-linked list of the queue.
        Returns if such order causes the TOB to change.
        """
        order_head, order_tail = order[7]
        order_price = order[4]
        if order_head: order_head[1] = order_tail
        if order_tail: order_tail[0] = order_head
        level = self.levels[order_price]
        level[3] -= 1
        
        if not level[3]:
            del self.levels[order[4]]
            if order_price == self.topOfBook[0]:
                self.topOfBook = self.bestPriceQty
            return True
        
        return False
                
    def remove_order(self, order):
        """
        Removes order from the book's doubly-linked list.
        """
        self.cancel_order(order)
        self.purge_order(order)