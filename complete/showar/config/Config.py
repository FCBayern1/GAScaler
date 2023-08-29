import time
from kubernetes import client, config
import base64
import os

def getNowTime():
    return int(round(time.time()))

class Config():
    def __init__(self):
        self.namespace = 'default'
        # self.nodes = {
        #     'ubuntu-Precision-Tower-7810': '192.168.31.202:9100',
        #     'dell': '192.168.31.201:9100',
        #     'node1': '192.168.31.136:9100'
        # }

        self.SLO = 200
        # maximum and minimum number of pods for a microservice
        self.max_pod = 8
        self.min_pod = 1

        # k8s config path
        self.k8s_config = './config.yaml'
        self.k8s_yaml = './exp_test_deployment.yaml'
        
        # set the duration of experiment
        self.duration = 1 * 20 * 60 # 20 min
        self.start = getNowTime()
        self.end = self.start + self.duration

        # prometheus
        self.prom_range_url = "http://localhost:9090/api/v1/query_range"
        self.prom_no_range_url = "http://localhost:9090/api/v1/query"
        self.step = 5