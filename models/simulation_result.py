class SimulationResult:
    def __init__(self, rate, success_rate):
        self.rate = rate
        self.success_rate = success_rate

    def to_dict(self):
        return {'rate': self.rate, 'success': self.success_rate}
