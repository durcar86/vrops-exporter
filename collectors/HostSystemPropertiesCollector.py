from BaseCollector import BaseCollector
import os, time, json
from prometheus_client.core import GaugeMetricFamily
from tools.Resources import Resources
from tools.YamlRead import YamlRead


class HostSystemPropertiesCollector(BaseCollector):
    def __init__(self):
        self.wait_for_inventory_data()
        self.property_yaml = YamlRead('collectors/property.yaml').run()
        self.g = GaugeMetricFamily('vrops_hostsystem_properties', 'testtest',
                              labels=['datacenter', 'vccluster', 'hostsystem', 'propkey'])

    def describe(self):
        yield self.g

    def collect(self):
        if os.environ['DEBUG'] >= '1':
            print('HostSystemPropertiesCollector starts with collecting the metrics')

        for target in self.get_hosts_by_target():
            token = self.get_target_tokens()
            token = token[target]

            if not token:
                print("skipping " + target + " in HostSystemPropertiesCollector, no token")

            uuids = self.target_hosts[target]
            for property_pair in self.property_yaml['HostSystemPropertiesCollector']['number_metrics']:
                property_label = property_pair['label']
                propkey = property_pair['property']
                values = Resources.get_latest_number_properties_multiple(target, token, uuids, propkey)
                if not values:
                    continue
                for value_entry in values:
                    data = value_entry['data']
                    host_id = value_entry['resourceId']
                    self.g.add_metric(
                        labels=[self.hosts[host_id]['datacenter'], self.hosts[host_id]['parent_cluster_name'],
                                self.hosts[host_id]['name'], property_label],
                        value=data)

            for property_pair in self.property_yaml["HostSystemPropertiesCollector"]['enum_metrics']:
                property_label = property_pair['label']
                propkey = property_pair['property']
                expected_state = property_pair['expected']
                values = Resources.get_latest_enum_properties_multiple(target, token, uuids, propkey, expected_state)
                if not values:
                    continue
                for value_entry in values:
                    data = value_entry['data']
                    host_id = value_entry['resourceId']
                    latest_state = value_entry['latest_state']
                    self.g.add_metric(
                        labels=[self.hosts[host_id]['datacenter'], self.hosts[host_id]['parent_cluster_name'],
                                self.hosts[host_id]['name'], property_label + ": " + latest_state],
                        value=data)

            for property_pair in self.property_yaml["HostSystemPropertiesCollector"]['info_metrics']:
                property_label = property_pair['label']
                propkey = property_pair['property']
                values = Resources.get_latest_info_properties_multiple(target, token, uuids, propkey)
                if not values:
                    continue
                for value_entry in values:
                    host_id = value_entry['resourceId']
                    try:
                        info_value = float(value_entry['data'])
                        self.g.add_metric(
                            labels=[self.hosts[host_id]['datacenter'], self.hosts[host_id]['parent_cluster_name'],
                                    self.hosts[host_id]['name'], property_label],
                            value=info_value)
                    except ValueError:
                        info = value_entry['data']
                        info_value = 0
                        self.g.add_metric(
                            labels=[self.hosts[host_id]['datacenter'], self.hosts[host_id]['parent_cluster_name'],
                                    self.hosts[host_id]['name'], property_label + ": " + info],
                            value=info_value)

            yield self.g


