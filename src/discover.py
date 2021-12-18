
import time
import subprocess
import _thread
from loguru import logger


class WLEDFinder:
    
    _instance = None

    def __init__(self):
        self.found = {}

    def _execute(self, command):
        result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, text=True)
        return result.stdout

    def _service_thread(self):
        while True:
            lines = [_ for _ in self._execute("avahi-browse -atp").split() if '_wled._tcp' in _]
            for line in lines:
                parts = line.split(';')
                # logger.debug(parts)
                name = f"{parts[3]}.{parts[5]}"
                if name not in self.found:
                    logger.debug(name)
                    try:
                        self.found[name] = self._execute(f'avahi-resolve --name {name}').split()[-1]
                    except:
                        logger.error(f"Failed to look up IP for {name}")
            time.sleep(60)

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = WLEDFinder()
            _thread.start_new_thread(cls._instance._service_thread, ())
        
        return cls._instance


