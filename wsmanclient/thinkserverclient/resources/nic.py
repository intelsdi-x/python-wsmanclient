import collections
import logging
import re

from wsmanclient import exceptions
from wsmanclient.thinkserverclient.resources import uris
from wsmanclient import utils
from wsmanclient import wsman

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
