
from sortedcontainers import SortedList

class MarginManager:
    def __init__(self, _master, mpid, contractID):
        self.priceLevels = [SortedList(key=lambda x:-x), SortedList()]
        self.qtyAtPrices = [{}, {}]
        self.exclRed = [0, 0]
        self.inc = [0, 0]

        self.orders = _master.orders[mpid]

        user_positions = _master.userPositions[mpid]
        if not contractID in user_positions: user_positions[contractID] = [[0, 0], [0, 0]]
        self.position, self.reducible = user_positions[contractID]

    def change_level(self, price, side, red, inc):
        price_level = self.priceLevels[side]
        qtys = self.qtyAtPrices[side]

        if not price in qtys:
            qtys[price] = [red, inc]
            price_level.add(price)
            if red and not inc: self.exclRed[side] += 1
            if inc: self.inc[side] += 1
            return

        qty_at_price = qtys[price]
        prev_contains_red = bool(qty_at_price[0])
        prev_contains_inc = bool(qty_at_price[1])
        prev_exclred = prev_contains_red and (not prev_contains_inc)

        qty_at_price[0] += red
        qty_at_price[1] += inc

        cur_exclred = (qty_at_price[0] and not qty_at_price[1])
        if not prev_exclred and cur_exclred: self.exclRed[side] += 1
        if prev_exclred and not cur_exclred: self.exclRed[side] -= 1

        if not (prev_contains_inc) and qty_at_price[1]: self.inc[side] += 1
        if prev_contains_inc and (not qty_at_price[1]): self.inc[side] -= 1