import os

class Config(object):
    # If not set fall back to production for safety
    FLASK_ENV =  os.getenv('FLASK_ENV', 'production')
    # Set FLASK_SECRET on your production Environment
    SECRET_KEY = os.getenv('FLASK_SECRET', 'Secret')
    SESSION_TYPE = os.getenv('FLASK_SESSION_TYPE', 'filesystem')

    APP_DIR = os.path.dirname(__file__)
    ROOT_DIR = os.path.dirname(APP_DIR)
    DIST_DIR = os.path.join(ROOT_DIR, 'front-end-dist')

    DISCOVERED_LED_FILE = '/tmp/discovered_leds.json'

    @classmethod
    def is_production(cls):
        return cls.FLASK_ENV.lower() == 'production'
