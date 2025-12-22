# order structure
# 0 - orderID
# 1 - timestamp
# 2 - mpid
# 3 - instrumentID
# 4 - price
# 5 - side
# 6 - [red, inc]
# 7 - [head, tail]

from new.OrderBook import OrderBook as OrderBook

class NashCore:
    def __init__(self, userBalances={}, userOrders={}, userPositions={}, contracts={}):
        # Ensure data integrity:
        # All user balances are initialised with available margin equal to the balance in order to have the margin manager do the work properly;
        # All userIDs, orderIDs and contractIDs are integers;

        self.userBalances = {int(user_id):[balance, balance] for user_id, balance in userBalances.items()}
        self.userOrders = {int(user_id):{int(order_id):order for order_id, order in indv_orders} for user_id, indv_orders in userOrders.items()}
        self.contractInformation = {int(contract_id):contract_information for contract_id, contract_information in contracts.items()}
        self.userPositions = {int(user_id):{int(contract_id):[position[:], position[:]] for contract_id, position in user_positions.items()} for user_id, user_positions in userPositions.items()}