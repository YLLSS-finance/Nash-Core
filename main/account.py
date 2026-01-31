
# DEPRECATED

# ORDER SCHEMA
# 0 | timestamp
# 1 | mpid
# 2 | contractID
# 3 | price
# 4 | side
# 5 | qty
# 6 | head order
# 7 | tail order

from position import position

class account:
    def __init__(self, _master, _mpid):
        raise Exception('This is deprecated')
        
        # [balance, margin]
        self._master = _master
        self.mpid = int(_mpid)
        
        self.balance = [0, 0]
        self.orders = {}
        self.availableOrderSlots = set([i for i in range(0, 20)])
        
        self.positions = {}
        
    def place_order(self, timestamp, contract, price, side, qty):
        '''
        This Function assumes that the inputs are correct, i.e. the price and side are proper and the contract code exists
        '''
        
        if not self.availableOrderSlots:
            return 050 # no available order slots
        
        order_id = self.availableOrderSlots.pop()
        
        if not contract in self.marginManagers:
            self.positions[contract] = position(user_balance=self.balance)
        
        if self.positions[contract].insert_order(price, side, qty):
            self.orders[self.availableOrderSlots] = [
                timestamp, 
                self.mpid, 
                contract, 
                price, 
                side, 
                qty, 
                None, 
                None
            ]
            
    # current fill order operation: look up the trader ID in the server accounts dictionary and fill orders through this function in the specific account
    
    def fill_order(self, order_id, price, qty):
        order_id = int(order_id)
        
        order = self.orders[order_id]
        order_contract = order[2]
        order_price = order[3]
        order_side = order[4]
        
        self.positions[order_contract].fill_order(order_price, order_side, price, qty)
        order[5] -= qty
        if not order[5]:
            del self.orders[order_id]
            self.availableOrderSlots.add(order_id)