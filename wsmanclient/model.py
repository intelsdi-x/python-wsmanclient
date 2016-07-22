import json


class StatusedResource(object):
    """
    An interface defining resource with an id and health status ('HealthStatus')
    """
    def __init__(self, id, status):
        self.id = id
        self.status = status
    def __repr__(self):
        return json.dumps(self.__dict__)

class CPU(StatusedResource): pass
#  id', 'cores', 'speed', 'ht_enabled', 'model', 'status', 'turbo_enabled',
#  'vt_enabled'
        
class Memory(StatusedResource): pass
#  'id', 'size', 'speed', 'manufacturer', 'model', 'status'

class PSU(StatusedResource): pass
# See iDRAC Service Module - Windows Management Instrumentation.pdf for
# more fields available
#  'id', 'description', 'last_system_inventory_time', 'last_update_time',
#  'primary_status'

class NICInterface(StatusedResource): pass
#  'id', 'description', 'product_name', 'mac_address', 'linkspeed'

class BootMode(StatusedResource): pass
#  'id', 'name', 'is_current', 'is_next'

class BootDevice(StatusedResource): pass
#  'id',  'boot_mode', 'current_assigned_sequence','pending_assigned_sequence',
#  bios_boot_string'

class Job(StatusedResource): pass
#  'id', 'name', 'start_time', 'until_time','message', 'state',
#  'percent_complete'

class PhysicalDisk(StatusedResource): pass
#  'id', 'description', 'controller', 'manufacturer', 'model', 'media_type',
#  'interface_type', 'size_mb', 'free_size_mb', 'serial_number',
#  'firmware_version', 'state', 'raid_state'

class RAIDController(StatusedResource): pass
#  'id', 'description', 'manufacturer', 'model','firmware_version'

class VirtualDisk(StatusedResource): pass
#  'id', 'name', 'description', 'controller', 'raid_level', 'size_mb','state',
#  'raid_state', 'span_depth', 'span_length', 'pending_operations'
