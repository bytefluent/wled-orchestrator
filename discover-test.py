
import time

import os
import sys
import pathlib

# Put every folder below this in the path.
[sys.path.insert(0, str(pathlib.Path(d[0]))) for d in os.walk(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))]

from discover import WLEDFinder
finder = WLEDFinder.instance()

while True:
    time.sleep(1)
