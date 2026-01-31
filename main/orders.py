
# ORDER SCHEMA
# 0 | timestamp
# 1 | mpid
# 2 | contractID
# 3 | price
# 4 | side
# 5 | qty
# 6 | head order 
# 7 | tail order

import numpy as np

class orders: 
    def __init__(self, books, account_positions, orders_per_account, cache_accounts):
        self.ordersPerAccount = orders_per_account
        self.cacheAccounts = cache_accounts
        
        self.orderBooks = books
        self.accountPositions = account_positions
        self.orders = np.empty(orders_per_account * cache_accounts, dtype=np.int32)
        
        self.initialAlloc = [i for i in range(0, orders_per_account)]
        
        # mpid:[starting_index, set(available_orders), set(used_orders)]
        self.accountMapping = {}
        
    def add_account(self, mpid):
        if mpid in self.accountMapping: return 
        
        existing_accounts = len(self.accountMapping.keys())
        if existing_accounts == self.cacheAccounts:
            raise Exception('Cache allocation exceeded: Please allocate more and restart the Nash instance.')
        
        self.accountMapping[mpid] = [len(self.accountMapping.keys()) * 8 * self.ordersPerAccount, set(self.initialAlloc), set()]

    def add_order(self, mpid, instrumentID, price, side, qty):
        instrumentID = int(instrumentID)
        mpid = int(mpid)
        if not instrumentID in self.orderBooks: 
            return 450
        
        if not mpid in self.accountMapping:
            return 400
        
        start_index, avbl_slots, used_slots = self.accountMapping[mpid]
        if not avbl_slots:
            return 050
        
        order_id = avbl_slots.pop()
        
            