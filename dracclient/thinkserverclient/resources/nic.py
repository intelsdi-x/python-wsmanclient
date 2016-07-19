import collections
import logging
import re

from dracclient import exceptions
from dracclient.thinkserverclient.resources import uris
from dracclient import utils
from dracclient import wsman

LOG = logging.getLogger(__name__)

STATUS_MAP = {
    "0": "Unknown",
    "2": "Enabled",
    "3": "Disabled"
}

NICInterface = collections.namedtuple(
    'NICInterface', ['id', 'description', 'product_name',
                     'mac_address', 'linkspeed'])


class NICManagement(object):

    def __init__(self, client):
        raise NotImplementedError
