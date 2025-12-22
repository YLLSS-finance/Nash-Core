
# order structure
# 0 - orderID
# 1 - timestamp
# 2 - mpid
# 3 - instrumentID
# 4 - price
# 5 - side
# 6 - [red, inc]
# 7 - [head, tail]

from new.orderProperties import OrderProperties as op
from new.MarginManager import MarginManager as MarginManager
from new.OrderBook import OrderBook as OrderBook

class NashCore:
    def __init__(self, userBalances={}, userOrders={}, userPositions={}, contracts={}):
        self.userBalances = userBalances
        self.userOrders = userOrders
        self.userPositions = userPositions
        self.userMarginManagers = {}
        self.contracts = {int(contractID):contractContents for contractID, contractContents in contracts.items()}
        self.orderBooks = {contractID:OrderBook() for OrderBook in self.contracts}

        self.setup()

    def setup(self):
        """
        Initialises proper user available margin(s), available position(s)

        """
        for user, user_balance in self.userBalances.items():
            required_margin_managers = set()

            if not user in self.userOrders:
                self.userOrders[user] = {}

            user_balance[:] = [user_balance[0], user_balance[0]]
            user_orders = self.userOrders[user]
            user_positions = self.userPositions[user]
            self.userMarginManagers[user] = {}
            user_margin_managers = self.userMarginManagers[user]

            for contract, user_contract_position in user_positions.items():
                user_contract_position[:] = [user_contract_position[0][:], user_contract_position[0][:]]
                required_margin_managers.add(contract)

            for order in user_orders.items():
                user_balance[1] -= op.TotalCost(order)
                if not order[3] in user_positions:
                    user_positions[order[3]] = [[0, 0], [0, 0]]
                required_margin_managers.add(order[3])
                user_positions[order.instrument][1][1 - order[5]] -= order[6][0]
                order[7] = [None, None]

            for margin_manager_contract in required_margin_managers:
                user_margin_managers[margin_manager_contract] = MarginManager(_master=self, mpid=user, contractID=margin_manager_contract)

        def _fillOrder(self, order, price, qty):
            order_side = order[5]
            order_margin_manager = self.userMarginManagers[order[2]][order[3]]
            fill_red = min(qty, order[6][0])
            fill_inc = qty - fill_red

            if fill_red == order[6][0]: order_margin_manager.reduceOrders[order_side] -= 1
            if fill_inc == order[6][1]: order_margin_manager.increaseOrders[order_side] -= 1

            price_improvement = abs(price - order[4])

        def _cancelOrder(self, order):
            order_margin_manager = self.userMarginManagers[order[2]][order[3]]
            order_side = order[5]
            if order[6][0]: order_margin_manager.reduceOrders[order_side] -= 1
            if order[6][1]: order_margin_manager.increaseOrders[order_side] -= 1

            del self.userOrders[order[2]][order[3]][order[0]]