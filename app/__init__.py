import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask

app = Flask(__name__, template_folder='templates')
app.config.from_object('config.Config')


from app import routes