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
    def best_price_qty(self):
        if self.levels:
            price, lvlInfo = self.levels.peekitem(0)
            return [price, lvlInfo[2]]
        return
    
    def initialize(self, orders):
        # Add initial list of orders to a unsorted dictionary, keyed by price.
        orders_dict = {}
        for order in orders:
            # At each price level there is an unsorted list of orders
            if not order[4] in orders_dict:
                orders_dict[order[4]] = []
            orders_dict[order[4]].append(order)

        # Sort all orders at each price level by price-time priority. 
        # The keys do not have to be sorted as this can be done by the SortedDict library for no relative overhead
        for order_list in orders_dict:
            order_list.sort(key=lambda x:x[1])

        # Purge any current information in the queue and reconstruct from the sorted-queue dictionary
        self.levels.clear()
        self.topOfBook = None
        for price_level, orders_at_level in orders_dict.items():
            # Iterate over orders at each level to determine the sum of their quantities.
            total_qty = sum([sum(order[6]) for order in orders_at_level])
            total_orders = len(orders_at_level)
            # [head=first order in list, tail=last order in list, sum of all order quantities, number of orders]
            self.levels[price_level] = [orders_at_level[0], orders_at_level[-1], total_qty, total_orders]

        self.topOfBook = self.best_price_qty
    
    def fill_top(self, price, qty):
        filled_qty = 0        
        while True:
            # No fill can be done if the book ie empty or if there is no quantity left to fill
            if not self.topOfBook: break
            if not qty: break
            
            best_price = self.topOfBook[0]
            
            # Book must be locked or crossing to trigger a fill
            if self.side == 0:
                if price > best_price: break
            else:
                if price < best_price: break
            
            # Fetch the order at the head of the top-of-book time queue, called the best order.
            best_order = self.levels[best_price][0]
            
            # Determine maximum quantity that can be filled
            fill_qty = min(qty, sum(best_order[6]))
            
            self.fill_order(best_order, best_price, fill_qty)
            
            # If the best order is filled, purge that order and break the loop if the top-of-book is changed 
            # as for this function we only want to try and fill at the best level available.
            if not sum(best_order[6]):
                tob_changed = self.purge_order(best_order)
                if tob_changed: break
            
            # Update variables
            qty -= fill_qty
            filled_qty += fill_qty
        
        return best_price, filled_qty
    
    def post_order(self, order):
        order_price = order[4]
        order_qty = sum(order[6])
        
        if not order_price in self.levels:
            # Setting up the head/tail/quantities at the new price level.
            # The order is the first at the new price level. Thus the head and tail are both that order
            self.levels[order_price] = [order, order, order_qty, 1]
            
            order_price_qty = [order_price, order_qty]
            
            # Initialising or Updating the top-of-book.
            
            # Small optimisation:
            # Note that we know that the price level is the best one, as well as the price/quantity of the new order
            # Thus we can simply set it according to the order to remove the overhead of calling self.best_price_qty!
            
            # If the order queue is empty before the addition of the new order, set the top-of-book
            if self.topOfBook is None:
                self.topOfBook = order_price_qty
                return
            
            # If a top-of-book already exists but the price of the new order improves it, update it
            if self.side == 0:
                if order_price > self.topOfBook[0]: self.topOfBook = order_price_qty
            else:
                if order_price < self.topOfBook[0]: self.topOfBook = order_price_qty
            return
        
        # The original tail order now has the new order behind it, update accordingly
        level = self.levels[order_price]
        level_tail = level[1]
        level_tail[7][1] = order
        
        # An item inserted to the end of a linked list has the original tail as its head and no tail
        order[7] = [level_tail, None]
        
        # Update tail of price level to the new order
        level[1] = order
        
        # Update quantities of cumulative order quantity and number of orders
        level[2] += order_qty
        level[3] += 1
    
    def purge_order(self, order):
        """
        Removes an order from the doubly-linked list of the queue.
        Returns if such order causes the TOB to change.
        """
        
        order_head, order_tail = order[7]
        order_price = order[4]
        
        # Remove order in doubly-linked list
        if order_head: order_head[1] = order_tail
        if order_tail: order_tail[0] = order_head
        
        # Decrease amount of orders at level by 1
        level = self.levels[order_price]
        level[3] -= 1
        
        if not level[3]:
            del self.levels[order_price]
            
            # For removing the last order at the top-of-book level we also need to update the top-of-book
            if order_price == self.topOfBook[0]:
                self.topOfBook = self.best_price_qty
            return True
        
        return False
                
    def remove_order(self, order):
        """
        Removes order from the book's doubly-linked list.
        """
        self.cancel_order(order)
        self.purge_order(order)