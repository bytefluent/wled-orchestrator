
import time
from loguru import logger

from zeroconf import ServiceBrowser, Zeroconf


class WLEDFinder:
    
    _instance = None

    def __init__(self):
        self.zeroconf = Zeroconf()
        browser = ServiceBrowser(self.zeroconf, "_wled._tcp.local.", self)
        self.found = {}

    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            logger.info(f"Service {name} updated, address: {info.addresses}, port: {info.port}")

    def remove_service(self, zeroconf, type, name):
        logger.info(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)

        self.found[name] = info._ipv4_addresses[0].compressed
        if info:
            logger.info(f"Service {name} added, address: {info.addresses}, port: {info.port}")


    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = WLEDFinder()
        
        return cls._instance


