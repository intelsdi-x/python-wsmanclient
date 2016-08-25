import collections
import logging
import re

from wsmanclient import exceptions, utils, wsman
from wsmanclient.model import NICInterface
from wsmanclient.thinkserverclient import constants
from wsmanclient.thinkserverclient.resources import uris

LOG = logging.getLogger(__name__)

STATUS_MAP = {
    "0": "Unknown",
    "2": "Enabled",
    "3": "Disabled"
}

class NICManagement(object):

    def __init__(self, client):
        """Creates NICManagement object

        :param client: an instance of WSManClient
        """
        self.client = client

    def list_nic_interfaces(self):
        """Returns the list of NIC interfaces

        :returns: a list of NIC inteface objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """

        doc = self.client.enumerate(uris.CIM_NetworkPort)
        
        nic_interfaces = doc.find(
            './/s:Body/wsen:EnumerateResponse/wsman:Items',
            wsman.NS_MAP)

        return [self._parse_nic_interfaces(interface)
                for interface in nic_interfaces]

    def _parse_nic_interfaces(self, nic_interface):
        return NICInterface(
            self._get_nic_interface_attr(nic_interface, 'DeviceID'),
            #  constants.HealthState[int(self._get_nic_interface_attr(nic_interface, 'HealthState'))],
            self._get_nic_interface_attr(nic_interface, 'HealthState'),
        )

    def _get_nic_interface_attr(self, nic_interface, attr_name):
        return utils.get_wsman_wsinst_resource_attr(
            nic_interface, uris.CIM_EthernetPort, attr_name)
