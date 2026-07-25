import math
import random

random.seed(42)

class BlockBootstrap:
    @staticmethod
    def get_bootstrap_sequence(data, total_months):
        n_blocks = 1
        max_start = len(data) - total_months
        sequence = []
        start = random.randint(0, max(0, max_start))
        sequence.extend(data[start : start + total_months])
        return sequence[:total_months]
