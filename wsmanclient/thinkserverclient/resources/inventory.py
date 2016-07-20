#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections

from wsmanclient.thinkserverclient.resources import uris
from wsmanclient import utils
from wsmanclient import wsman
from wsmanclient.thinkserverclient import constants

from wsmanclient.model import CPU, Memory

class InventoryManagement(object):

    def __init__(self, client):
        """Creates InventoryManagement object

        :param client: an instance of WSManClient
        """
        self.client = client

    def list_cpus(self):
        """Returns the list of CPUs

        :returns: a list of CPU objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
        """

        doc = self.client.enumerate(uris.CIM_Processor)

        cpus = doc.find('.//s:Body/wsen:EnumerateResponse/wsman:Items',
                wsman.NS_MAP)

        return [self._parse_cpus(cpu) for cpu in cpus]

    def _parse_cpus(self, cpu):
        return CPU(self._get_cpu_attr(cpu, 'DeviceID'),
                status=constants.CPUStatus[self._get_cpu_attr(cpu, 'CPUStatus')])

    def _get_cpu_attr(self, cpu, attr_name):
        return utils.get_wsman_wsinst_resource_attr(cpu, uris.CIM_Processor, attr_name)

    def list_memory(self):
        """Returns the list of installed memory

        :returns: a list of Memory objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
        """

        doc = self.client.enumerate(uris.CIM_PhysicalMemory)

        installed_memory = doc.find('.//s:Body/wsen:EnumerateResponse/wsman:Items',
                wsman.NS_MAP)

        return [self._parse_memory(memory) for memory in installed_memory]

    def _parse_memory(self, memory):
        return Memory(self._get_memory_attr(memory, 'ElementName'),
                status=constants.HealthState[self._get_memory_attr(memory, 'HealthState')])

    def _get_memory_attr(self, memory, attr_name):
        return utils.get_wsman_wsinst_resource_attr(memory, uris.CIM_PhysicalMemory, attr_name)
