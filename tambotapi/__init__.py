r"""The Powerful TamTam Bot API Framework"""
from __future__ import print_function

import logging
import os
import pickle
import re
import sys
import threading
import time
import six

# Logger
logger = logging.getLogger('tambotapi')
log_format = logging.Formatter('%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"')
console_output_handler = logging.StreamHandler(sys.stderr)
console_output_handler.setFormatter(log_format)
logger.addHandler(console_output_handler)
logger.setLevel(logging.ERROR)

from . import util, apihandler

