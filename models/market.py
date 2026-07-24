class MarketState:
    def __init__(self, row):
        self.year = int(row['year'])
        self.month = int(row['month'])
        self.us_return = float(row['us_stock_return'])
        self.us_dividend = float(row['us_stock_dividend'])
        self.intl_return = float(row['intl_stock_return'])
        self.intl_dividend = float(row['intl_stock_dividend'])
        self.bond_return = float(row['bond_return'])
        self.bond_interest_rate = float(row['bond_interest_rate'])
        self.inflation = float(row['inflation'])
        self.hysa_interest = float(row['hysa_interest'])
