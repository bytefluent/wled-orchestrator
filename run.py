import os
import sys
import pathlib

# Put every folder below this in the path.
[sys.path.insert(0, str(pathlib.Path(d[0]))) for d in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))]

from server import server, socketio
from config import Config

def run():
    socketio.run(server, host='0.0.0.0', port=8889, debug=(not Config.is_production()))

if __name__ == "__main__":
    run()

# To Run:
# python run.py
# or
# python -m flask run%  