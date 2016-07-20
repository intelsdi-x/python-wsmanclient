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

DMTF_RESERVED = 'DMTF Reserved'
VENDOR_RESERVED = 'Vendor Reserved'

EnabledState = {
        None: 'Unknown (Error)',
        0: 'Unknown',
        1: 'Other',
        2: 'Enabled',
        3: 'Disabled',
        5: 'Shutting Down',
        5: 'Not Applicable',
        6: 'Enabled but Offline',
        7: 'In Test',
        8: 'Deferred',
        9: 'Quiesce',
        10: 'Starting',
        }

def _get_enabled_state(state_id):
    id_int = int(state_id)
    if(id_int < 11):
        return EnabledState[id_int]
    elif(11 <= id_int <= 32767):
        return DMTF_RESERVED
    elif(32768 <= id_int <= 65535):
        return VENDOR_RESERVED

HealthState = {
        None: 'Unknown (Error)',
        0: 'Unknown',
        5: 'OK',
        10: 'Degraded/Warning',
        15: 'Minor failure',
        20: 'Major failure',
        25: 'Critical failure',
        30: 'Non-recoverable error',
        }

def _get_health_state(state_id):
    id_int = int(state_id)
    if(id_int <= 30):
        return HealthState[id_int]
    elif(30 < id_int <= 32767):
        return DMTF_RESERVED
    elif(32768 <= id_int <= 65535):
        return VENDOR_RESERVED

CPUStatus = {
        None: 'Unknown (Error)',
        '0': 'Unknown',
        '1': 'CPU Enabled',
        '2': 'CPU Disabled by User',
        '3': 'CPU Disabled By BIOS (POST Error)',
        '4': 'CPU Is Idle',
        '7': 'Other',
        }
