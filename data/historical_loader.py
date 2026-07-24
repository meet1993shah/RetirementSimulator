import csv
from config import Config

class HistoricalLoader:
    @staticmethod
    def load_dataset():
        dataset = []
        # utf-8-sig ensures any Byte Order Marks (BOM) from Excel/Sheets are stripped
        with open(Config.CSV_PATH, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dataset.append(row)
        return dataset
