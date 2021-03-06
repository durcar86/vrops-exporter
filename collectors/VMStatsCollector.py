from BaseCollector import BaseCollector
import os
from prometheus_client.core import GaugeMetricFamily
from tools.Resources import Resources
from tools.YamlRead import YamlRead


class VMStatsCollector(BaseCollector):
    def __init__(self):
        self.wait_for_inventory_data()
        self.statkey_yaml = YamlRead('collectors/statkey.yaml').run()
        # self.post_registered_collector(self.__class__.__name__, g.name)

    def describe(self):
        yield GaugeMetricFamily('vrops_vm_stats', 'testtext')

    def collect(self):
        g = GaugeMetricFamily('vrops_vm_stats', 'testtext', labels=['vccluster', 'datacenter', 'virtualmachine', 'hostsystem', 'statkey'])
        if os.environ['DEBUG'] >= '1':
            print('VMStatsCollector starts with collecting the metrics')

       # #make one big request per stat id with all resource id's in its belly
        for target in self.get_vms_by_target():
            token = self.get_target_tokens()
            token = token[target]
            if not token:
                print("skipping " + target + " in VMStatsCollector, no token")

            uuids = self.target_vms[target]
            for statkey_pair in self.statkey_yaml["VMStatsCollector"]:
                statkey_label = statkey_pair['label']
                statkey = statkey_pair['statkey']
                values = Resources.get_latest_stat_multiple(target, token, uuids, statkey)
                if not values:
                    print("skipping statkey " + str(statkey) + " in VMStatsCollector, no return")
                    continue
                for value_entry in values:
                    if 'resourceId' not in value_entry:
                        continue
                    #there is just one, because we are querying latest only
                    metric_value = value_entry['stat-list']['stat'][0]['data']
                    if not metric_value:
                        continue
                    vm_id = value_entry['resourceId']
                    if vm_id not in self.vms:
                        continue
                    g.add_metric(labels=[self.vms[vm_id]['cluster'], self.vms[vm_id]['datacenter'],
                                self.vms[vm_id]['name'], self.vms[vm_id]['parent_host_name'], statkey_label],
                                 value=metric_value[0])
        # self.post_metrics(g.name)
        yield g
