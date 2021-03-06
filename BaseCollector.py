from abc import ABC, abstractmethod
import requests
import time
import os

class BaseCollector(ABC):

    @abstractmethod
    def collect(self):
        pass

    def get_vcenters(self):
        current_iteration = self.get_iteration()
        url = "http://localhost:8000/vcenters/{}".format(current_iteration)
        request = requests.get(url)
        self.vcenters = request.json()
        return self.vcenters

    def get_datacenters(self):
        current_iteration = self.get_iteration()
        url = "http://localhost:8000/datacenters/{}".format(current_iteration)
        request = requests.get(url)
        self.datacenters = request.json()
        return self.datacenters

    def get_clusters(self):
        current_iteration = self.get_iteration()
        url = "http://localhost:8000/clusters/{}".format(current_iteration)
        request = requests.get(url)
        self.clusters = request.json()
        return self.clusters

    def get_hosts(self):
        current_iteration = self.get_iteration()
        url = "http://localhost:8000/hosts/{}".format(current_iteration)
        request = requests.get(url)
        self.hosts = request.json()
        return self.hosts

    def get_datastores(self):
        current_iteration = self.get_iteration()
        url = "http://localhost:8000/datastores/{}".format(current_iteration)
        request = requests.get(url)
        self.datastores = request.json()
        return self.datastores

    def get_vms(self):
        current_iteration = self.get_iteration()
        url = "http://localhost:8000/vms/{}".format(current_iteration)
        request = requests.get(url)
        self.vms = request.json()
        return self.vms

    def get_iteration(self):
        request = requests.get(url = "http://localhost:8000/iteration")
        self.iteration = request.json()
        return self.iteration

    def get_targets(self):
        request = requests.get(url="http://localhost:8000/vrops_list")
        self.target = request.json()
        return self.target

    def get_target_tokens(self):
        request = requests.get(url="http://localhost:8000/target_tokens")
        self.target_tokens = request.json()
        return self.target_tokens

    def post_registered_collector(self, collector, *metric_names):
        payload = {
            'collector': collector,
            'metric_names': list(metric_names)
        }
        request = requests.post(json=payload, url="http://localhost:8000/register")
        if request.status_code != 200:
            print("request failed with status: {}".format(request.status_code))

    def get_registered_collectors(self):
        request = requests.get(url="http://localhost:8000/register")
        self.collectors_up = request.json()
        return self.collectors_up

    def post_metrics(self, metric):
        payload = {
            'metric_name': metric
        }
        r = requests.post(json=payload, url="http://localhost:8000/metrics")
        if r.status_code != 200:
            print("request failed with status: {}".format(r.status_code))

    def get_metrics(self):
        request = requests.get(url="http://localhost:8000/metrics")
        self.metrics = request.json()
        return self.metrics

    def delete_metrics(self):
        request = requests.delete(url="http://localhost:8000/metrics")
        if request.status_code != 200:
            print("request failed with status: {}".format(request.status_code))

    def get_clusters_by_target(self):
        if not hasattr(self, 'target_clusters'):
            self.target_clusters = dict()
        cluster_dict = self.get_clusters()
        for uuid in cluster_dict:
            cluster = cluster_dict[uuid]
            if cluster['target'] not in self.target_clusters:
                self.target_clusters[cluster['target']] = list()
            self.target_clusters[cluster['target']].append(uuid)
        return self.target_clusters

    def get_hosts_by_target(self):
        if not hasattr(self, 'target_hosts'):
            self.target_hosts = dict()
        host_dict = self.get_hosts()
        for uuid in host_dict:
            host = host_dict[uuid]
            if host['target'] not in self.target_hosts:
                self.target_hosts[host['target']] = list()
            self.target_hosts[host['target']].append(uuid)
        return self.target_hosts

    def get_datastores_by_target(self):
        if not hasattr(self, 'target_datastores'):
            self.target_datastores = dict()
        datastore_dict = self.get_datastores()
        for uuid in datastore_dict:
            host = datastore_dict[uuid]
            if host['target'] not in self.target_datastores:
                self.target_datastores[host['target']] = list()
            self.target_datastores[host['target']].append(uuid)
        return self.target_datastores

    def get_vms_by_target(self):
        if not hasattr(self, 'target_vms'):
            self.target_vms = dict()
        vms_dict = self.get_vms()
        for uuid in vms_dict:
            vm = vms_dict[uuid]
            if vm['target'] not in self.target_vms:
                self.target_vms[vm['target']] = list()
            self.target_vms[vm['target']].append(uuid)
        return self.target_vms

    def wait_for_inventory_data(self):
        iteration = 0
        while not iteration:
            time.sleep(5)
            iteration = self.get_iteration()
            if os.environ['DEBUG'] >= '1':
                print("waiting for initial iteration: " + type(self).__name__)
        print("done: initial query " + type(self).__name__)
        return
