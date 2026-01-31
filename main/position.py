from sortedcontainers import SortedDict


class position:
    # This is the position and margin management engine for LVIS Nash.
    # All operations related to position and margin manipulations are handled by this class.
    # Note that margin is dynamically recalculated with each operation to reflect the total exposure caused by open order, 
    # while the user balance only changes when an order is filled, reducing an existing position or increasing it.
    
    def __init__(self, user_balance):
        self.userBalance = user_balance

        self.position = [0, 0]
        self.reducible = [0, 0]

        self.levels = [SortedDict(), SortedDict()]
        self.redLevels = [0, 0]
<<<<<<< HEAD

        self.cost_function = [lambda x: x, lambda x: 100 - x]

=======
        
        self.cost_function = [lambda x:x, lambda x:100 - x]
        self.price_mapping = [lambda x:-x, lambda x:x]
        
>>>>>>> a97ee9f7515196441d153f2fe5db13a2e04b2157
    def debug(self):
        print("Balances\n", self.userBalance, "\n")
        print("Position\n", self.position, "\n")
        print("Reducible\n", self.reducible, "\n")
        print("Levels\n", self.levels, "\n")
        print("Reduce Levels\n", self.redLevels, "\n")

    def insert_order(self, price, side, qty):
<<<<<<< HEAD
        # List of Data Manipulations performed
        #
        # Split the order quantity into an reduce and increase component
        #
        # Check if the order price is defective (see below)
        # If so, proceed to fix it by allocating the increase component of the order to order levels on the same side that has a better (higher if buy and lower if sell) price than the incoming order, until there are no such better prices left or the entire increase component of the order has been reallocaed
        # During this operation, price improvement occurs. Return the margin saved bec33333

        order_red = min(self.reducible[1 - side], qty)
        order_inc = qty - order_red

        op_red = order_red
        margin_used = self.cost_function[side](price) * order_inc

        ins_price = -price if side == 0 else price

        side_levels: SortedDict = self.levels[side]

        swaps = []
        # If there is a violation, iterate through the levels containing reduce orders from worst to best
        # and perform swap operations between the inc quantity of the new order and the red quantities
        # of the existing levels
        for n in range(self.redLevels[side] - 1, -1, -1):
            if not order_inc:
                break

            lvl_price, lvl_qtys = side_levels.peekitem(n)
            lvl_price: int

            if (side == 0 and -lvl_price >= price) or (
                side == 1 and lvl_price <= price
            ):
                break
            swap_qty = min(order_inc, lvl_qtys[0])
            if not swap_qty:
                break

            swaps.append([lvl_qtys, swap_qty])
            order_inc -= swap_qty
            order_red += swap_qty

            margin_used -= abs(abs(lvl_price) - price) * swap_qty

        if margin_used + self.userBalance[1] > self.userBalance[0]:
=======
        
        # Split the order into an reduce and increase component based on the reducible quantity on the opposite side, and calculate the initial margin used
        order_red = min(self.reducible[1 - side], qty)
        order_inc = qty - order_red
        op_red = order_red
        margin_used = self.cost_function[side](price) * order_inc
        
        side_levels = self.levels[side]
        swaps = []        
        
        # Iterate over all levels with reduce orders in reverse order (price from worst to best)
        for n in range(self.redLevels[side] - 1, -1, -1):
            # Check if the order has an increase component and the price level to scan has an reduce component
            if not order_inc: break
            lvl_price, lvl_qtys = side_levels.peekitem(n)
            if not lvl_qtys[0]: break
            
            # Check if the price of the incoming order is better than the price of the existing level in the iteration
            if (side == 0 and -lvl_price < price) or (side == 1 and lvl_price > price):
                swap_qty = min(order_inc, lvl_qtys[0])    
                swaps.append([lvl_qtys, swap_qty])
                
                order_inc -= swap_qty
                order_red += swap_qty
                    
                margin_used -= abs(abs(lvl_price) - price) * swap_qty
        
        if margin_used > self.userBalance[1]:
>>>>>>> a97ee9f7515196441d153f2fe5db13a2e04b2157
            return False

        self.userBalance[1] += margin_used

        for lvl_qtys, swap_qty in swaps:
            lvl_red = bool(lvl_qtys[0])
            lvl_qtys[0] -= swap_qty
            lvl_qtys[1] += swap_qty

            if lvl_red and (not lvl_qtys[0]):
                self.redLevels[side] -= 1
<<<<<<< HEAD

        if ins_price not in side_levels:
=======
        
        ins_price = self.price_mapping[side](price)
        
        if not ins_price in side_levels:
>>>>>>> a97ee9f7515196441d153f2fe5db13a2e04b2157
            side_levels[ins_price] = [0, 0]
            if order_red:
                self.redLevels[side] += 1

        order_lvl = side_levels[ins_price]
        order_lvl[0] += order_red
        order_lvl[1] += order_inc

        self.reducible[1 - side] -= op_red

        return True

    def remove_order(self, price, side, qty):
        level_price = -price if side == 0 else price

        side_levels = self.levels[side]
        order_price_level = side_levels[level_price]
        prev_red = bool(order_price_level[0])

        remove_inc = min(qty, order_price_level[1])
        remove_red = qty - remove_inc
        order_price_level[0] -= remove_red
        order_price_level[1] -= remove_inc

        self.userBalance[1] += remove_inc * self.cost_function[side](price)

        self.reducible[1 - side] += remove_red
        self.alloc_reducible_position()

        if prev_red and (not order_price_level[0]):
            self.redLevels[side] -= 1

        if not sum(order_price_level):
            del side_levels[level_price]

    def alloc_reducible_position(self):
        # List of Data Manipulations conducted
        # In order of the level price from best to worst, allocate the reducible position into levels with an increase component in the opposite side of the reducible position

        # Margin manipulation: Return the margin for orders in the level where the allocation from increase to reduce component was performed
<<<<<<< HEAD

        alloc_side = 0 if self.reducible[0] else 1
        if self.reducible[1 - alloc_side]:
            raise Exception(
                "Fatal Error: There exists a reducible component on both sides of the position"
            )

        side_levels = self.levels[1 - alloc_side]
        reducible_to_net = self.reducible[alloc_side]
        start_loc = self.redLevels[1 - alloc_side] - 1
        if start_loc == -1:
            return

=======
        
        alloc_side = 1 if self.reducible[0] else 0
        if self.reducible[alloc_side]: 
            raise Exception('Fatal Error: There exists a reducible component on both sides of the position')
        
        side_levels = self.levels[alloc_side]
        reducible_to_net = self.reducible[1 - alloc_side]
        start_loc = self.redLevels[alloc_side] - 1
        if start_loc == -1: return 
        
>>>>>>> a97ee9f7515196441d153f2fe5db13a2e04b2157
        for n in range(start_loc, len(side_levels.keys())):
            lvl_price, lvl_qtys = side_levels.peekitem(n)
            if not lvl_qtys[1]:
                continue

            net_qty = min(lvl_qtys[1], reducible_to_net)
            if not net_qty:
                break

            lvl_qtys[0] += net_qty
            lvl_qtys[1] -= net_qty

            # Refund the margin for the order price level that had a quantity moved from the increase side to the reduce side
<<<<<<< HEAD
            self.userBalance[1] -= net_qty * self.cost_function[1 - alloc_side](
                lvl_price
            )

=======
            self.userBalance[1] += net_qty * self.cost_function[alloc_side](lvl_price)
    
    
>>>>>>> a97ee9f7515196441d153f2fe5db13a2e04b2157
    def fill_order(self, order_price, order_side, fill_price, fill_qty):
        level_price = -order_price if order_side == 0 else order_price

        order_level = self.levels[order_side][level_price]
        if fill_qty > sum(order_level):
            raise Exception('Fatal accounting error: Order fill quantity exceeded total quantity at the level of the order price in account position manager')
        
        fill_red = min(fill_qty, order_level[0])
        fill_inc = fill_qty - fill_red

        price_improvement = abs(fill_price - order_price)

        margin_returned = (
            fill_inc * price_improvement
        )  # Increase the available margin by this amount, this is caused by price improvement

        fill_cost = self.cost_function[order_side](fill_price) * fill_inc
        reduce_revenue = self.cost_function[1 - order_side](fill_price) * fill_red

        order_level[0] -= fill_red
        order_level[1] -= fill_inc

        self.position[order_side] += fill_inc
        self.position[1 - order_side] -= fill_red
        self.reducible[order_side] += fill_inc

        if fill_inc:
            self.alloc_reducible_position()

        # TODO: Please review this balance change for integrity
        self.userBalance[1] += margin_returned + reduce_revenue
        self.userBalance[0] += reduce_revenue - fill_cost

<<<<<<< HEAD

balance = [10000, 10000]
=======
>>>>>>> a97ee9f7515196441d153f2fe5db13a2e04b2157

def test():
    # basic unit test for the position and margin manager
    balance = [10000, 10000]

    pos = position(balance)
    pos.position = [0, 50]
    pos.reducible = [0, 50]
    pos.insert_order(70, 0, 80)
    pos.insert_order(75, 0, 70)
    pos.insert_order(72, 0, 15)

<<<<<<< HEAD
pos.remove_order(75, 0, 10)
pos.debug()
=======
    pos.fill_order(75, 0, 70, 60)
    pos.debug()

    pos.remove_order(75, 0, 10)
    pos.debug()
>>>>>>> a97ee9f7515196441d153f2fe5db13a2e04b2157
