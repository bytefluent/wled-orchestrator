
from loguru import logger

import time
import datetime
import math
import json
import requests

# wleds = []

from db import LEDsGroupTable, PatternTable

group_table = LEDsGroupTable()
pattern_table = PatternTable()

class Schedule(object):
    def __init__(self):
        self.strings = []
        self.start = 0
        self.end = 0
        self.enabled = False

        self._pattern_index = 0
        self._pattern_expiration = 0
        self._pattern_list = []

    def seconds_today(self):
        day_time = datetime.datetime.now().time()
        seconds = (day_time.hour * 60 * 60) + (day_time.minute * 60)
        return seconds

    def step(self):
        if not self.enabled:
            self._pattern_expiration = 0
            return
        
        now = self.seconds_today()
        shutdown = True
        if self.start < self.end:
            # basic interval
            shutdown = now < self.start or now > self.end
        else:
            # the interval spans midnight.
            shutdown = now > self.end and now < self.start
        try:
            if shutdown:
                for led_string in self.strings:
                    if led_string not in LedString.strings: continue
                    string = LedString.strings[led_string]
                    string.power(False)
                return

            if self._pattern_expiration <= time.time():
                # logger.info(f"Stepping pattern.. {self.start} {self.seconds_today()} {self.end}")
                self._pattern_index = (self._pattern_index + 1) % len(self._pattern_list)
                # logger.info(f"Next pattern index {self._pattern_index}")
                next_pattern = self._pattern_list[self._pattern_index]
                # logger.info(f"Next pattern {next_pattern}")
                self._pattern_expiration = time.time() + int(next_pattern['duration'])
                for led_string in self.strings:
                    if led_string not in LedString.strings: continue
                    string = LedString.strings[led_string]
                    string.set_pattern(next_pattern['pattern'], pattern_table.by_id(next_pattern['pattern']))
                    string.on = True
        except Exception as e:
            self._pattern_expiration = 0
            logger.exception(e)

    @classmethod
    def from_row(self, row):
        schedule = Schedule()
        schedule.start = row['start_time']
        schedule.end = row['end_time']
        schedule.enabled = bool(row['enabled'])
        all_groups = group_table.get_all()
        groups = {g['id']: g for g in all_groups}
        for group_id in row['string_json']:
            schedule.strings.extend(groups[group_id]['group_json'])
        schedule._pattern_list = row['effects_json']

        return schedule


from db import LEDsTable

class LedString(object):
    strings = {}

    effects = []
    palettes = []

    def __init__(self, server, addr):
        logger.debug(f"Now managing! {server} {addr}")

        self.table = LEDsTable()
        self.row = dict()
        self.strings[server] = self
        self.strings[addr] = self
        self.server = server
        self.addr = addr
        self.on = None
        self.speed = None
        self.intensity = None
        self.color1 = None
        self.color2 = None
        self.color3 = None

        self.effect = None
        self.palette = None

        self.data = dict(info=dict(uptime=0))

        self.update_pending = False
        self.last_refresh = 0

        self.sync_db()

        if not LedString.effects:
            logger.debug("Fetching Effects!")
            LedString.effects = self._get("effects")
            logger.warning(LedString.effects)

        if not LedString.palettes:
            logger.debug("Fetching Palettes!")
            LedString.palettes = self._get("palettes")
            logger.warning(LedString.palettes)

    def needs_refresh(self):
        return time.time() > self.last_refresh + 20

    def sync_db(self):
        self.row = self.table.by_name(self.server)
        if not self.row:
            new_string = dict(
                name=self.server,
                addr=self.addr,
                ip_addr=None,
                first_time=time.time(),
                last_time=time.time(),
                current_pattern=None)
            self.table.insert(new_string)
            self.row = self.table.by_name(self.server)

    def _get(self, path):
        request_path = f"http://{self.addr}/json/{path}"
        # logger.debug(request_path)
        result = requests.get(request_path)
        # logger.debug(result.text)
        try:
            return result.json()
        except json.decoder.JSONDecodeError:
            logger.error("Failed to parse JSON!")
            logger.warning(result.text)
            return None

    def refresh_info(self):
        self.last_refresh = time.time()

        info = self._get("info")
        if info['uptime'] < self.data['info']['uptime']:
            logger.debug(info)
            logger.warning(f"There was an unexpected restart! {self.server}, {self.addr} ({info['uptime']} < {self.data['info']['uptime']})")
            # new_data['state'] = self.data['state']
            self.update_pending = True

        self.data["info"] = info
        self.strings[self.data['info']['name']] = self

    def refresh_state(self):

        state = self._get("state")
        self.data['state'] = state

        self.on = self.data['state']['on']

        self.color1 = self.data['state']['seg'][0]['col'][0]
        self.color2 = self.data['state']['seg'][0]['col'][1]
        self.color3 = self.data['state']['seg'][0]['col'][2]

        self.speed = self.data['state']['seg'][0]['sx']
        self.intensity = self.data['state']['seg'][0]['ix']

        self.effect = self.effects[self.data['state']['seg'][0]['fx']]
        self.palette = self.palettes[self.data['state']['seg'][0]['pal']]

    def power(self, on = True):
        # logger.debug(f"power {self.on} {on} {self.update_pending}")
        if on != self.on:
            self.on = on
            self.update_pending = True

    def refresh(self):
        # logger.info("Refreshing")
        self.refresh_info()
        self.refresh_state()

        self.row = self.table.by_name(self.server)

    def update(self):
        # print(self.data)

        self.update_pending = False
        try:
            self.last_refresh = 0
            segment_up = {
                "fx": self.effect_id(self.effect),
                "pal": self.palette_id(self.palette),
                "col": [self.color1, self.color2, self.color3],
                "sx": self.speed,
                "ix": self.intensity,
                "on": self.on
            }
            # logger.debug(segment_up)
            result = requests.post(f"http://{self.addr}/json/state", data=json.dumps(
                {"on": self.on, "seg":[segment_up]}), headers={'content-type':'application/json'})
            result.raise_for_status()
        except Exception as e:
            logger.error(e)
            return

    def set_pattern(self, pattern_id, data):
        if pattern_id:
            self.table.update_pattern(self.server, pattern_id)
            self.row["current_pattern"] = pattern_id

        self.color1 = data.get('color1', self.color1) or self.color1
        self.color2 = data.get('color2', self.color2) or self.color2
        self.color3 = data.get('color3', self.color3) or self.color3
        self.effect = data.get('effect', self.effect) or self.effect
        self.palette = data.get('palette', self.palette) or self.palette
        self.intensity = data.get('intensity', self.intensity)
        self.speed = data.get('speed', self.speed)

        self.update_pending = True

    def get_pattern(self):
        return dict(
            color1=self.color1,
            color2=self.color2,
            color3=self.color3,
            effect=self.effect,
            palette=self.palette,
            intensity=self.intensity,
            speed=self.speed
        )

    # def effects(self):
    #     return self.effects

    def effect_id(self, name):
        return self.effects.index(name)

    # def palettes(self):
    #     return self.palettes

    def palette_id(self, name):
        return self.palettes.index(name)

    def to_json(self):
        ret = dict(
            server=self.server,
            addr=self.addr,
            data=self.data,
            pattern=self.row.get("current_pattern"),
        )
        ret.update(self.row)

        return ret

