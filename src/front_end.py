""" Client App """

import os
from flask import Blueprint, render_template
from config import Config

front_end = Blueprint(
    'front_end',
    __name__,
    url_prefix='',
    static_url_path='',
    static_folder=Config.DIST_DIR
)