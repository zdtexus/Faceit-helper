import os


class Config:
    FACEIT_API_KEY = os.environ.get('FACEIT_API_KEY')
    STEAM_API_KEY = os.environ.get('STEAM_API_KEY') 
    TELEGRAM_API_KEY = os.environ.get('TELEGRAM_API_KEY') 