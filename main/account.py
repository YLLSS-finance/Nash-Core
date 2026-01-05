
class account:
    def __init__(self, _master):
        # [balance, margin]
        self._master = _master
        
        self.balance = [0, 0]
        self.orders = {}
        self.positions = {}
        self.marginManagers = {}
        
    