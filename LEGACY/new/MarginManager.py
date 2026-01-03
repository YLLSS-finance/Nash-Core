
# order structure
# 0 - orderID
# 1 - timestamp
# 2 - mpid
# 3 - instrumentID
# 4 - price
# 5 - side
# 6 - [red, inc]
# 7 - [head, tail] 

from sortedcontainers import SortedList
from LEGACY.new.orderProperties import OrderProperties as op

class MarginManager:
    def __init__(self, _master, mpid, contractID):
        self.contractID = contractID
        self.mpid = mpid

        self.position, self.reducible = _master.userPositions[contractID]
        self.userOrders = _master.userOrders[contractID]
        self.userBalances = _master.userBalances[mpid]

        self.contractOrders = [SortedList(key=op.BuyOrderComparator) , SortedList(key=op.SellOrderComparator)]
        self.reduceOrders = [0, 0]
        self.increaseOrders = [0, 0]

        self.contractOrderBook = _master.orderBook[contractID]

        for order in self.userOrders:
            if order[3] == self.contractID:
                order_side = order[5]
                 # Add order into the sorted list
                self.contractOrders[order_side].add(order)
                self.reducible[1 - order_side] -= order[6][0]
                self.userBalances[1] -= op.TotalCost(order)
                if order[6][0]: self.reduceOrders[order_side] += 1
                if order[6][1]: self.increaseOrders[order_side] += 1
    
    def add_balance(self, qty):
        self.
    
    def add_order(self, timestamp, orderID, price, side, qty):
        red = min(qty - self.reducible[1 - side])
        inc = qty - red

        order = [orderID, timestamp, self.mpid, self.contractID, price, side, [], []]
        queue_position = op.BuyOrderComparator if side == 0 else op.SellOrderComparator

        # Swap: new order inc-->red | existing order red --> inc
        cur_redorders = self.reduceOrders[side]
        transfer_lst = []
        if inc and cur_redorders:
            cur_contractorders = self.contractOrders[side]
            for existing_order_index in range(cur_redorders, -1, -1):
                existing_order = cur_contractorders[existing_order_index]
                if queue_position(existing_order) < queue_position(order) or not inc: break
                transfer = min(inc, existing_order[0])
                transfer_lst += [existing_order, transfer]

                inc -= transfer
                red += transfer

        required_margin = inc * op.ContractCost(order)
        if required_margin < self.userBalances[1]:
            return False

        self.userBalances[1] -= required_margin
        # actually do the swap operation after the margin is confirmed to be sufficient
        for old_order, qty in transfer_lst:
            old_order[6][0] -= qty
            old_order[6][1] += qty

        order[6] = [red, inc]
        self.contractOrderBook.addOrder(order)
        self.userOrders[int(orderID)] = order
        if red: self.reduceOrders[side] += 1
        if inc: self.increaseOrders[side] += 1

        return True

    def allocReducible(self):
        alloc_side = 0 if self.reducible[0] else 1
        if self.reducible[1 - alloc_side]:
            raise Exception('Fatal error: there is somehow a reducible position on both sides. Please halt all affected markets immediately.')

        reducible = self.reducible[alloc_side]
        order_list, red_orders, inc_orders = self.contractOrders[1 - alloc_side], self.reduceOrders[1 - alloc_side], self.increaseOrders[1 - alloc_side]

        if red_orders == len(order_list):
            return
        if red_orders > len(order_list):
            raise Exception('Fatal error: the amount of reduce orders as indicated by the red_orders[order_side] exceeds the amount of orders in the order list')

        for order_id in range(len(order_list) - inc_orders, len(order_list)):
            order = order_list[order_id]
            alloc_qty = min(order[6][1], reducible)
            order[6][1] -= alloc_qty
            order[6][0] += alloc_qty
            reducible -= alloc_qty

            self.userOrders[1] += op.ContractCost(order) * alloc_qty