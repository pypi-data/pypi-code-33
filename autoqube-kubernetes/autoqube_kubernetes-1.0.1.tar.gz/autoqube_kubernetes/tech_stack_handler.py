from pymongo import MongoClient
from pprint import pprint

MOCK = True


class TechStackHandler:
    def __init__(self, config=None):
        if config is None:
            self.mongo_client = MongoClient()
        else:
            self.mongo_client = MongoClient(config['host'], config['port'])
        self._db = self.mongo_client['autoqube']
        self._collection = self._db['k8_stacks']

    def create_new_stack(self, stack):
        result = self._collection.insert_one(stack)
        return result.inserted_id

    def get_stack_list(self):
        stack_list = list()
        result = self._collection.find({}, {"stack": 1})
        for stack in result:
            stack_list.append(stack['stack'])
        return stack_list

    def get_stack(self, stack_name):
        if MOCK:
            return sample_stack
        result = self._collection.find_one({"stack": stack_name})
        return result


sample_stack = {
    "stack": "jmeter",
    "workload_templates": {
        "Slave": {
            "Deployment": {
                "yaml": "jmeter_slaves_deploy.yaml",
                "status": True
            },
            "Service": {
                "yaml": "jmeter_slaves_svc.yaml",
                "status": True
            }
        },
        "Master": {
            "Configmap": {
                "yaml": "jmeter_master_configmap.yaml",
                "status": False
            },
            "Deployment": {
                "yaml": "jmeter_master_deploy.yaml",
                "status": True
            }
        },
        "InfluxDB": {
            "Configmap": {
                "yaml": "jmeter_influxdb_configmap.yaml",
                "status": False
            },
            "Deployment": {
                "yaml": "jmeter_influxdb_deploy.yaml",
                "status": True
            },
            "Service": {
                "yaml": "jmeter_influxdb_svc.yaml",
                "status": True
            }
        },
        "Grafana": {
            "Configmap": {
                "yaml": "jmeter_grafana_configmap.yaml",
                "status": False
            },
            "Deployment": {
                "yaml": "jmeter_grafana_deploy.yaml",
                "status": True
            },
            "Service": {
                "yaml": "jmeter_grafana_svc.yaml",
                "status": True
            }
         }
    },
    "deployment_order": {
        "1": {
            "service": "Slave",
            "timeout": 0
        },
        "2": {
            "service": "Master",
            "timeout": 0
        },
        "3": {
            "service": "InfluxDB",
            "timeout": 0
        },
        "4": {
            "service": "Grafana",
            "timeout": 0
        }
    },
    "commands": {
        "influxdb": {
            "commands": ["influx -execute 'CREATE DATABASE jmeter'"]
        },
        "grafana": {
            "commands": ["curl 'http://admin:admin@127.0.0.1:3000/api/datasources' "
                         "-X POST -H 'Content-Type: application/json;charset=UTF-8' "
                         "--data-binary "
                         "'{\"name\":\"jmeterdb\",\"type\":\"influxdb\",\"url\":\"http://jmeter-influxdb:8086\","
                         "\"access\":\"proxy\",\"isDefault\":true,\"database\":\"jmeter\",\"user\":\"admin\","
                         "\"password\":\"admin\"}'"]
        }
    },
    "test_files": {
        "master": {
            "destination_location": "/tmp/"
        }
    },
    "test_commands": {
        "master": {
            "commands": ["sh /root/load_test /tmp/{test_file}"]
        }
    },
    "list_services": {
        "grafana": {
            "message": "Please visit '{load_balancer_ingress_hostname}:3000' to check grafana dashboards"
        }
    }
}
