import collections
import logging
import re

from wsmanclient import exceptions
from wsmanclient.dracclient.resources import uris
from wsmanclient import utils
from wsmanclient import wsman

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

        doc = self.client.enumerate(uris.DCIM_NICView)

        drac_nic_interfaces = utils.find_xml(doc, 'DCIM_NICView',
                                             uris.DCIM_NICView,
                                             find_all=True)

        return [self._parse_drac_nic_interfaces(interface)
                for interface in drac_nic_interfaces]

    def _parse_drac_nic_interfaces(self, drac_nic_interface):
        return NICInterface(
            id=self._get_nic_interface_attr(drac_nic_interface, 'FQDD'),
            description=self._get_nic_interface_attr(
                drac_nic_interface, 'DeviceDescription'),
            product_name=self._get_nic_interface_attr(
                drac_nic_interface, 'ProductName'),
            mac_address=self._get_nic_interface_attr(
                drac_nic_interface, 'PermanentMACAddress'),
            linkspeed=self._get_nic_interface_attr(
                drac_nic_interface, 'LinkSpeed')
        )

    def _get_nic_interface_attr(self, drac_nic_interface, attr_name):
        return utils.get_wsman_resource_attr(
            drac_nic_interface, uris.DCIM_NICView, attr_name)


class NICAttribute(object):
    """Generic NIC attribute class"""

    namespace = uris.DCIM_NICAttribute

    def __init__(self, fqdd, name, current_value, pending_value, read_only):
        """Creates NICAttribute object
        :param fqdd: fqdd of network interface
        :param name: name of the NIC attribute
        :param current_value: current value of the NIC attribute
        :param pending_value: pending value of the NIC attribute, reflecting
                an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this NIC attribute can be changed
        """

        self.fqdd = fqdd
        self.name = name
        self.current_value = current_value
        self.pending_value = pending_value
        self.read_only = read_only

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @classmethod
    def parse(cls, namespace, nic_attr_xml):
        """Parses XML and creates NICAttribute object"""

        fqdd = utils.get_wsman_resource_attr(
            nic_attr_xml, namespace, 'FQDD', nullable=True)
        name = utils.get_wsman_resource_attr(
            nic_attr_xml, namespace, 'AttributeName')
        current_value = utils.get_wsman_resource_attr(
            nic_attr_xml, namespace, 'CurrentValue', nullable=True)
        pending_value = utils.get_wsman_resource_attr(
            nic_attr_xml, namespace, 'PendingValue', nullable=True)
        read_only = utils.get_wsman_resource_attr(
            nic_attr_xml, namespace, 'IsReadOnly')

        return cls(fqdd, name, current_value, pending_value, (read_only == 'true'))


class NICEnumerableAttribute(NICAttribute):
    """Enumerable NIC attribute class"""

    namespace = uris.DCIM_NICEnumeration

    def __init__(self, fqdd, name, current_value, pending_value, read_only,
                 possible_values):
        """Creates NICEnumerableAttribute object

        :param name: name of the NIC attribute
        :param current_value: current value of the NIC attribute
        :param pending_value: pending value of the NIC attribute, reflecting
                an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this NIC attribute can be changed
        :param possible_values: list containing the allowed values for the NIC
                                attribute
        """
        super(NICEnumerableAttribute, self).__init__(fqdd, name, current_value,
                                                     pending_value, read_only)
        self.possible_values = possible_values

    @classmethod
    def parse(cls, nic_attr_xml):
        """Parses XML and creates NICEnumerableAttribute object"""
        nic_attr = NICAttribute.parse(cls.namespace, nic_attr_xml)
        possible_values = [attr.text for attr
                           in utils.find_xml(nic_attr_xml, 'PossibleValues',
                                             cls.namespace, find_all=True)]

        return cls(nic_attr.fqdd, nic_attr.name, nic_attr.current_value,
                   nic_attr.pending_value, nic_attr.read_only,
                   possible_values)

    def validate(self, new_value):
        """Validates new value"""

        if str(new_value) not in self.possible_values:
            msg = ("Attribute '%(attr)s' cannot be set to value '%(val)s'."
                   " It must be in %(possible_values)r.") % {
                       'attr': self.name,
                       'val': new_value,
                       'possible_values': self.possible_values}
            return msg


class NICStringAttribute(NICAttribute):
    """String NIC attribute class"""

    namespace = uris.DCIM_NICString

    def __init__(self, fqdd, name, current_value, pending_value, read_only,
                 min_length, max_length, pcre_regex):
        """Creates NICStringAttribute object

        :param name: name of the NIC attribute
        :param current_value: current value of the NIC attribute
        :param pending_value: pending value of the NIC attribute, reflecting
                an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this NIC attribute can be changed
        :param min_length: minimum length of the string
        :param max_length: maximum length of the string
        :param pcre_regex: is a PCRE compatible regular expression that the
                           string must match
        """
        super(NICStringAttribute, self).__init__(fqdd, name, current_value,
                                                 pending_value, read_only)
        self.min_length = min_length
        self.max_length = max_length
        self.pcre_regex = pcre_regex

    @classmethod
    def parse(cls, nic_attr_xml):
        """Parses XML and creates NICStringAttribute object"""

        nic_attr = NICAttribute.parse(cls.namespace, nic_attr_xml)
        min_length = int(utils.get_wsman_resource_attr(
            nic_attr_xml, cls.namespace, 'MinLength'))
        max_length = int(utils.get_wsman_resource_attr(
            nic_attr_xml, cls.namespace, 'MaxLength'))
        pcre_regex = utils.get_wsman_resource_attr(
            nic_attr_xml, cls.namespace, 'ValueExpression', nullable=True)

        return cls(nic_attr.fqdd, nic_attr.name, nic_attr.current_value,
                   nic_attr.pending_value, nic_attr.read_only,
                   min_length, max_length, pcre_regex)

    def validate(self, new_value):
        """Validates new value"""

        if self.pcre_regex is not None:
            regex = re.compile(self.pcre_regex)
            if regex.search(str(new_value)) is None:
                msg = ("Attribute '%(attr)s' cannot be set to value '%(val)s.'"
                       " It must match regex '%(re)s'.") % {
                           'attr': self.name,
                           'val': new_value,
                           're': self.pcre_regex}
                return msg


class NICIntegerAttribute(NICAttribute):
    """Integer NIC attribute class"""

    namespace = uris.DCIM_NICInteger

    def __init__(self, fqdd, name, current_value, pending_value, read_only,
                 lower_bound, upper_bound):
        """Creates NICIntegerAttribute object

        :param name: name of the NIC attribute
        :param current_value: current value of the NIC attribute
        :param pending_value: pending value of the NIC attribute, reflecting
                an unprocessed change (eg. config job not completed)
        :param read_only: indicates whether this NIC attribute can be changed
        :param lower_bound: minimum value for the NIC attribute
        :param upper_bound: maximum value for the NIC attribute
        """
        super(NICIntegerAttribute, self).__init__(fqdd, name, current_value,
                                                  pending_value, read_only)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    @classmethod
    def parse(cls, nic_attr_xml):
        """Parses XML and creates NICIntegerAttribute object"""

        nic_attr = NICAttribute.parse(cls.namespace, nic_attr_xml)
        lower_bound = utils.get_wsman_resource_attr(
            nic_attr_xml, cls.namespace, 'LowerBound')
        upper_bound = utils.get_wsman_resource_attr(
            nic_attr_xml, cls.namespace, 'UpperBound')

        if nic_attr.current_value:
            nic_attr.current_value = int(nic_attr.current_value)
        if nic_attr.pending_value:
            nic_attr.pending_value = int(nic_attr.pending_value)

        return cls(nic_attr.fqdd, nic_attr.name, nic_attr.current_value,
                   nic_attr.pending_value, nic_attr.read_only,
                   int(lower_bound), int(upper_bound))

    def validate(self, new_value):
        """Validates new value"""

        val = int(new_value)
        if val < self.lower_bound or val > self.upper_bound:
            msg = ('Attribute %(attr)s cannot be set to value %(val)d.'
                   ' It must be between %(lower)d and %(upper)d.') % {
                       'attr': self.name,
                       'val': new_value,
                       'lower': self.lower_bound,
                       'upper': self.upper_bound}
            return msg


class NICConfiguration(object):

    def __init__(self, client):
        """Creates NICConfiguration object

        :param client: an instance of WSManClient
        """
        self.client = client

    def list_nic_settings(self, interface):
        """List the NIC configuration settings
        :param: interface: a string containing the FQDD of the network
                interface that is being polled
        :returns: a dictionary with the NIC settings using its name as the
                  key. The attributes are either NICEnumerableAttribute,
                  NICStringAttribute or NICIntegerAttribute objects.
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        """
        self.interface = interface
        result = {}
        namespaces = [(uris.DCIM_NICAttribute, NICAttribute),
                      (uris.DCIM_NICEnumeration, NICEnumerableAttribute),
                      (uris.DCIM_NICString, NICStringAttribute),
                      (uris.DCIM_NICInteger, NICIntegerAttribute),
                      ]
        for (namespace, attr_cls) in namespaces:
            attribs = self._get_config(namespace, attr_cls, self.interface)
            if not set(result).isdisjoint(set(attribs)):
                raise exceptions.DRACOperationFailed(
                    drac_messages=('Colliding attributes %r' % (
                        set(result) & set(attribs))))

            result.update(attribs)
        return result

    def _get_config(self, resource, attr_cls, interface):
        result = {}
        doc = self.client.enumerate(resource)
        items = doc.find('.//{%s}Items' % wsman.NS_WSMAN)
        if not items is None:
            for item in items:
                attribute = attr_cls.parse(item)
                if attribute.fqdd in interface:
                    result[attribute.name] = attribute
        return result

    def set_nic_settings(self, interface, new_settings):
        """Sets the NIC configuration

        To be more precise, it sets the pending_value parameter for each of the
        attributes passed in. For the values to be applied, a config job must
        be created and the node must be rebooted.

        :param new_settings: a dictionary containing the proposed values, with
                             each key being the name of attribute and the
                             value being the proposed value.
        :returns: a dictionary containing the commit_needed key with a boolean
                  value indicating whether a config job must be created for the
                  values to be applied.
        :raises: WSManRequestFailure on request failures
        :raises: WSManInvalidResponse when receiving invalid response
        :raises: DRACOperationFailed on error reported back by the DRAC
                 interface
        :raises: DRACUnexpectedReturnValue on return value mismatch
        :raises: InvalidParameterValue on invalid NIC attribute
        """
        self.interface = interface
        print interface
        current_settings = self.list_nic_settings(self.interface)
        unknown_keys = set(new_settings) - set(current_settings)
        if unknown_keys:
            msg = ('Unknown NIC attributes found: %(unknown_keys)r' %
                   {'unknown_keys': unknown_keys})
            raise exceptions.InvalidParameterValue(reason=msg)

        read_only_keys = []
        unchanged_attribs = []
        invalid_attribs_msgs = []
        attrib_names = []
        candidates = set(new_settings)
        print candidates
        for attr in candidates:
            if str(new_settings[attr]) == str(
                    current_settings[attr].current_value):
                unchanged_attribs.append(attr)
            elif current_settings[attr].read_only:
                read_only_keys.append(attr)
            else:
                validation_msg = current_settings[attr].validate(
                    new_settings[attr])
                if validation_msg is None:
                    attrib_names.append(attr)
                else:
                    invalid_attribs_msgs.append(validation_msg)

        if unchanged_attribs:
            LOG.warning('Ignoring unchanged NIC attributes: %r',
                        unchanged_attribs)

        if invalid_attribs_msgs or read_only_keys:
            if read_only_keys:
                read_only_msg = ['Cannot set read-only NIC attributes: %r.'
                                 % read_only_keys]
            else:
                read_only_msg = []

            drac_messages = '\n'.join(invalid_attribs_msgs + read_only_msg)
            raise exceptions.DRACOperationFailed(
                drac_messages=drac_messages)

        if not attrib_names:
            return {'commit_required': False}

        selectors = {'CreationClassName': 'DCIM_NICService',
                     'Name': 'DCIM:NICService',
                     'SystemCreationClassName': 'DCIM_ComputerSystem',
                     'SystemName': 'DCIM:ComputerSystem'}
        properties = {'Target': self.interface,
                      'AttributeName': attrib_names,
                      'AttributeValue': [new_settings[attr] for attr
                                         in attrib_names]}
        print properties
        doc = self.client.invoke(uris.DCIM_NICService, 'SetAttributes',
                                 selectors, properties)

        return {'commit_required': utils.is_reboot_required(
            doc, uris.DCIM_NICService)}
