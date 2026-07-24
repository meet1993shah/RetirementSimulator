import math
import random

random.seed(42)

class BlockBootstrap:
    @staticmethod
    def get_bootstrap_sequence(data, total_months, block_size_months):
        n_blocks = math.ceil(total_months / block_size_months)
        max_start = len(data) - block_size_months
        sequence = []
        for _ in range(n_blocks):
            start = random.randint(0, max(0, max_start))
            sequence.extend(data[start : start + block_size_months])
        return sequence[:total_months]
