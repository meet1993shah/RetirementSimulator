class Portfolio:
    def __init__(self, initial_value, us_alloc, intl_alloc, bond_alloc, initial_spending):
        self.total_value = float(initial_value)
        self.us_alloc = us_alloc
        self.intl_alloc = intl_alloc
        self.bond_alloc = bond_alloc
        
        # Initial cash buffer (12 months of annual spending held in HYSA)
        self.cash_buffer = float(initial_spending)
        invested = self.total_value - self.cash_buffer
        
        self.us_stocks = invested * self.us_alloc
        self.intl_stocks = invested * self.intl_alloc
        self.bonds = invested * self.bond_alloc

    @property
    def invested_pool(self):
        return self.us_stocks + self.intl_stocks + self.bonds

    def get_weights(self):
        inv = self.invested_pool
        if inv <= 0:
            return self.us_alloc, self.intl_alloc, self.bond_alloc
        return self.us_stocks / inv, self.intl_stocks / inv, self.bonds / inv
