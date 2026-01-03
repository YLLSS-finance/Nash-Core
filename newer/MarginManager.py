
from sortedcontainers import SortedDict

class MarginManager:
    def __init__(self, _master, mpid, contract_id):
        acct_positions = _master.acctPositions[mpid]
        if not contract_id in acct_positions:
            acct_positions[contract_id] = [[0, 0], [0, 0]]
        else:
            actual_position = acct_positions[contract_id][0]
            acct_positions[contract_id] = [actual_position[:], actual_position[:]]

        self.acctOrders = _master.acctOrders[mpid]
        self.position, self.reducible = acct_positions[contract_id]

    