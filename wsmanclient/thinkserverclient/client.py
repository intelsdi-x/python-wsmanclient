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

"""
Wrapper for pywsman.Client
"""

import logging

from wsmanclient import exceptions, utils, wsman
from wsmanclient.base_client import BaseClient
from wsmanclient.thinkserverclient.resources import (bios, inventory, job, nic,
                                                     uris)
from wsmanclient.wsman import WSManClient

LOG = logging.getLogger(__name__)

class ThinkServerClient(BaseClient):
    """Client for managing DRAC nodes"""

    BIOS_DEVICE_FQDD = 'BIOS.Setup.1-1'
    NIC_DEVICE_FQDD = 'NIC.Setup.1-1'

    def __init__(self, host, username, password, port=443, path='/wsman',
                 protocol='https'):
        """Creates client object

        :param host: hostname or IP of the DRAC interface
        :param username: username for accessing the DRAC interface
        :param password: password for accessing the DRAC interface
        :param port: port for accessing the DRAC interface
        :param path: path for accessing the DRAC interface
        :param protocol: protocol for accessing the DRAC interface
        """

        self.client = WSManClient(host, username, password, port, path,
                                  protocol)
        self._job_mgmt = job.JobManagement(self.client)
        self._power_mgmt = bios.PowerManagement(self.client)
        self._boot_mgmt = bios.BootManagement(self.client)
        self._bios_cfg = bios.BIOSConfiguration(self.client)
        self._nic_mgmt = nic.NICManagement(self.client)
        self._inventory_mgmt = inventory.InventoryManagement(self.client)

    def get_power_state(self):
        """Returns the current power state of the node

        :returns: power state of the node, one of 'POWER_ON', 'POWER_OFF' or
                  'REBOOT'
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """
        return self._power_mgmt.get_power_state()

    def set_power_state(self, target_state):
        raise NotImplementedError

    def list_power_supply_units(self):
        """Returns the list of PSUs

        :returns: list of BootMode objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """
        return self._power_mgmt.list_power_supply_units()

    def list_boot_modes(self):
        """Returns the list of boot modes

        :returns: list of BootMode objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """
        return self._boot_mgmt.list_boot_modes()

    def list_boot_devices(self):
        """Returns the list of boot devices

        :returns: a dictionary with the boot modes and the list of associated
                  BootDevice objects, ordered by the pending_assigned_sequence
                  property
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """
        return self._boot_mgmt.list_boot_devices()

    def change_boot_device_order(self, boot_mode, boot_device_list):
        raise NotImplementedError

    def list_bios_settings(self):
        raise NotImplementedError

    def set_bios_settings(self, settings):
        raise NotImplementedError

    def get_health_state(self):
        """Returns the current health state of the node

        :returns: health state of the node, one of 'UNKNOWN', 'OK', 'DEGRADED/WARNING' or 'ERROR'
        """
        return self._power_mgmt.get_health_state()

    def list_nic_interfaces(self):
        """Returns the list of nic interfaces

        :returns: a list of NICinterfaces objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """
        return self._nic_mgmt.list_nic_interfaces()

    def list_nic_settings(self, interface):
        raise NotImplementedError

    def set_nic_settings(self, interface, settings):
        raise NotImplementedError

    def list_jobs(self, only_unfinished=False):
        raise NotImplementedError

    def get_job(self, job_id):
        raise NotImplementedError
        
    def create_config_job(self, resource_uri, cim_creation_class_name,
                          cim_name, target,
                          cim_system_creation_class_name='DCIM_ComputerSystem',
                          cim_system_name='DCIM:ComputerSystem',
                          reboot=False):
        raise NotImplementedError

    def delete_pending_config(
            self, resource_uri, cim_creation_class_name, cim_name, target,
            cim_system_creation_class_name='DCIM_ComputerSystem',
            cim_system_name='DCIM:ComputerSystem'):
        raise NotImplementedError
        
    def commit_pending_bios_changes(self, reboot=False):
        raise NotImplementedError
        
    def abandon_pending_bios_changes(self):
        raise NotImplementedError
        
    def get_lifecycle_controller_version(self):
        raise NotImplementedError
        
    def list_raid_controllers(self):
        raise NotImplementedError

    def list_virtual_disks(self):
        raise NotImplementedError
        
    def list_physical_disks(self):
        raise NotImplementedError
        
    def convert_physical_disks(self, raid_controller, physical_disks,
                               raid_enable=True):
        raise NotImplementedError
        
    def create_virtual_disk(self, raid_controller, physical_disks, raid_level,
                            size_mb, disk_name=None, span_length=None,
                            span_depth=None):
        raise NotImplementedError

    def delete_virtual_disk(self, virtual_disk):
        raise NotImplementedError
        
    def commit_pending_raid_changes(self, raid_controller, reboot=False):
        raise NotImplementedError
        
    def abandon_pending_raid_changes(self, raid_controller):
        raise NotImplementedError

    def list_cpus(self):
        """Returns the list of CPUs

        :returns: a list of CPU objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """
        return self._inventory_mgmt.list_cpus()

    def list_memory(self):
        """Returns a list of memory modules

        :returns: a list of Memory objects
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """

        return self._inventory_mgmt.list_memory()
