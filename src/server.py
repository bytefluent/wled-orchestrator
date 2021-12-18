__version__ = '0.1.0'

import os
import json
import time
import traceback

import asyncio
import eventlet
eventlet.monkey_patch()

from flask import Flask, current_app, send_file, jsonify, request, session
from flask_socketio import SocketIO, emit

from loguru import logger

from db import initialize, PatternTable, SettingsTable, ScheduleTable, LEDsGroupTable

from front_end import front_end

initialize()

pattern_table = PatternTable()
settings_table = SettingsTable()
schedule_table = ScheduleTable()
groups_table = LEDsGroupTable()

settings_table['start'] = value=time.time()

server = Flask(__name__)
server.config.from_object('src.config.Config')
server.register_blueprint(front_end)
server.logger.info('>>> {}'.format(server.config['FLASK_ENV']))

socketio = SocketIO(server, cors_allowed_origins='*', async_mode="eventlet")

from led_string import LedString, Schedule
from discover import WLEDFinder
finder = WLEDFinder.instance()

leds = {}
schedules = []

schedule_mode_on = settings_table.get('schedule_on', False)
schedules = [Schedule.from_row(r) for r in schedule_table.get_all()]


@server.route('/')
def serve_front_end():
    """Default route. Serves the root page of the vue front-end"""
    dist_dir = current_app.config['DIST_DIR']
    entry = os.path.join(dist_dir, 'index.html')
    return send_file(entry)

@server.route('/static/<file>', methods=['GET'])
def serve_static(file):
    entry = os.path.join(current_app.config['ROOT_DIR'], 'files', file)
    return send_file(entry)


@logger.catch
def _thread_step():
    global schedules
    global schedule_mode_on
    found = list(finder.found.items())
    for name, addr in found:
        # Check to see if the LEDs on the network are being managed yet
        if name not in leds:
            leds[name] = LedString(name, addr)

    # logger.debug(schedule_mode_on)
    # logger.debug(schedules)
    if schedule_mode_on:
        for schedule in schedules:
            schedule.step()

    for lname, led in leds.items():
        if led.update_pending:
            led.update()
        if led.needs_refresh():
            led.refresh()
            socketio.emit("leds", [led.to_json()])

    #     wrapper.fill()
    # socketio.emit("inputs_delta", dict(changes=changes))

def _socketio_thread():
    while True:
        _thread_step()
        time.sleep(0.1)

socketio.start_background_task(_socketio_thread)

def exception_catch(socket_handler):
    def inner_function(*args, **kwargs):
        try:
            socket_handler(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception during {socket_handler}")
            emit('error', dict(args=args, kwargs=kwargs, exception=str(e), traceback=traceback.format_exc().splitlines()))
    return inner_function

@socketio.on('connect')
def client_connect():
    session["sid"] = request.sid
    emit('identify', dict(session)) # Ask the client to identify themselves

@socketio.on('disconnect')
def client_disconnect():
    # logger.info(request.sid)
    # logger.info(session)
    # if client := session.get('client'):
    #     broker_server.clients[client['id']].status = 'DISCONNECTED'
    logger.info('Client Disconnected')

@socketio.on('refresh')
def client_refresh():
    emit("leds", [led.to_json() for name, led in leds.items()])
    emit("settings", settings_table.all_as_dict())
    emit("state", dict(
        effects=LedString.effects,
        palettes=LedString.palettes,
        patterns=pattern_table.select_all(),
        schedules=schedule_table.get_all(),
        groups=groups_table.get_all()))

@socketio.on('update')
def client_update(data):
    logger.info(data)
    # led = leds[data['server']]
    for server, led in leds.items():
        if (data.get('server', server) or server) != server: continue
        led.set_pattern(None, data)
        print(json.dumps(led.get_pattern(), indent=2))

@socketio.on('command')
def client_command(data):
    global schedules
    global schedule_mode_on
    command = data.get('command')
    if command == 'save_pattern':
        led_id = data['server']
        led = leds[led_id]
        pattern = led.get_pattern()
        pattern["name"] = data.get('name', "-unnamed-")
        pattern["id"] = data.get("id")
        pattern = pattern_table.save(pattern)
        logger.info(f"New pattern id {pattern['id']}")
        led.set_pattern(pattern['id'], pattern)
    if command == 'set_pattern':
        pattern = pattern_table.by_id(data['id'])
        for server, led in leds.items():
            if (data.get('server', server) or server) != server: continue
            led.set_pattern(data['id'], pattern)
    if command == 'power':
        for server, led in leds.items():
            if (data.get('server', server) or server) != server: continue
            led.power(data['on'])
    if command == 'set_setting':
        settings_table[data['key']] = data['value']
        logger.debug(f"Settings setting[{data['key']}] = {data['value']}")
        if data['key'] == 'schedule_on':
            schedule_mode_on = settings_table.get('schedule_on', False)
            schedules = [Schedule.from_row(r) for r in schedule_table.get_all()]
        # logger.debug(leds.keys())
        emit("settings", settings_table.all_as_dict())

    if command == 'save_schedule':
        schedule_table.save(data['schedule'])
        schedules = [Schedule.from_row(r) for r in schedule_table.get_all()]

    if command == 'save_group':
        groups_table.save(data['group'])


@socketio.on('toggle')
def client_toggle(bit):
    logger.info(bit)



