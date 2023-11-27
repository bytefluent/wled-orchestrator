import json
import os
import sys
import time
import pathlib

# Put every folder below this in the path.
[sys.path.insert(0, str(pathlib.Path(d[0]))) for d in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))]

from config import Config

from discover import WLEDFinder
finder = WLEDFinder.instance()

if __name__ == "__main__":

    while True:
        time.sleep(15)
        json.dump(finder.found, open(Config.DISCOVERED_LED_FILE, 'w'))
