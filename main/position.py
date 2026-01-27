from sortedcontainers import SortedDict

class position:
    def __init__(self, user_balance):
        self.userBalance = user_balance
        
        self.position = [0, 0]
        self.reducible = [0, 0]
        
        self.levels = [SortedDict(), SortedDict()]
        self.redLevels = [0, 0]
        self.redBoundaryPrice = [None, None]
        
        self.cost_function = [lambda x:x, lambda x:100 - x]
        
    def net
        
    def insert_order(self, price, side, qty):
        ins_price = -price if side == 0 else price
        
        order_red = min(self.reducible[1 - side], qty)
        order_inc = qty - order_red
        op_red = order_red
        margin_used = self.cost_function[side](price)
        
        red_boundary = self.redBoundaryPrice[side]
        side_levels = self.levels[side]
        
        swaps = []
        
        # These 2 if statements can be removed if the red boundary price is proven to be unreliable or detrimental to performance
        if order_inc and (not red_boundary is None):
            if (side == 0 and price > -red_boundary) or (side == 1 and price < red_boundary):
                
                # If there is a violation, iterate through the levels containing reduce orders from worst to best
                # and perform swap operations between the inc quantity of the new order and the red quantities 
                # of the existing levels
                
                for n in range(self.redLevels[side] - 1, -1, -1):
                    if not order_inc: break
                    lvl_price, lvl_qtys = side_levels.peekitem(n)
                    if (side == 0 and -lvl_price >= price) or (side == 1 and lvl_price <= price): break
                    
                    swap_qty = min(order_inc, lvl_qtys[0])
                    if not swap_qty: break
                    
                    swaps.append([lvl_qtys, swap_qty])
                    order_inc -=  swap_qty
                    order_red += swap_qty
                    
                    margin_used -= abs(abs(lvl_price) - price) * swap_qty
                
        if margin_used > self.userBalance[1]:
            return False
    
        for lvl_qtys, swap_qty in swaps:
            lvl_red = bool(lvl_qtys[0])
            lvl_qtys[0] -= swap_qty
            lvl_qtys[1] += swap_qty
            
            if lvl_red and (not lvl_qtys[0]):
                self.redLevels[side] -= 1
        
        if not ins_price in side_levels:
            side_levels[ins_price] = [0, 0]
            if order_red: self.redLevels[side] += 1
        
        order_lvl = side_levels[ins_price]
        order_lvl[0] += order_red
        order_lvl[1] += order_inc
        
        self.reducible[1 - side] -= op_red
        
        return True

    def alloc_reducible_position(self):
        alloc_side = 0 if self.reducible[0] else 1
        if self.reducible[1 - alloc_side]: 
            raise Exception('Fatal Error: There exists a reducible component on both sides of the position')
        
        side_levels = self.levels[1 - alloc_side]
        reducible_to_net = self.reducible[alloc_side]
        for n in range(len(side_levels) - 1, -1, -1):
            lvl_price, lvl_qtys = side_levels.peekitem(n)
            net_qty = min(lvl_qtys[1], reducible_to_net)
            if not net_qty: break
            
            lvl_qtys[0] += net_qty
            lvl_qtys[1] -= net_qty
            
            # Refund the margin for the order price level that had a quantity moved from the increase side to the reduce side
            self.userBalance[1] += net_qty * self.cost_function[1 - alloc_side](lvl_price)
    
    def fill_order(self, order_price, order_side, fill_price, fill_qty):
        order_level = self.levels[order_side][order_price]
        fill_red = min(fill_qty, order_level[0])
        fill_inc = fill_qty - fill_red
        
        price_improvement = abs(fill_price - order_price)
        
        margin_returned = fill_inc * price_improvement # Increase the available margin bu this amount, this is caused by price improvement
        
        fill_cost = self.cost_function[order_side](order_price) * fill_inc
        
        self.position[order_side] += fill_inc
        self.position[1 - order_side] -= fill_red
        self.reducible[order_side] += fill_inc
        
        if fill_inc:
            self.alloc_reducible_position()
    
