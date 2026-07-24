import os

class Config:
    SECRET_KEY = os.urandom(24)
    DEBUG = True
    PORT = 5000
    HOST = '127.0.0.1'
    CSV_PATH = 'historical_monthly.csv'
