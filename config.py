import os

class Config:
    SECRET_KEY = os.urandom(24)
    DEBUG = False
    PORT = 8080
    HOST = '0.0.0.0'
    CSV_PATH = 'historical_monthly.csv'
