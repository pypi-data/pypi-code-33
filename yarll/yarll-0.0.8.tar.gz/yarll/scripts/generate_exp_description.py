#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import json

predef = {
    "experiment_name": "CartPole-KT",
    "environments": {
        "type": "json",
        "source": "Environment/random_CartPole_envs4.json"
    },
    "agent": {
        "name": "AsyncKnowledgeTransfer",
        "args": {
            "monitor_path": "/tmp/CartPole-v0-AKT",
            "video": False,
            "save_model": True,
            "monitor": True,
            "n_iter": 200,
            "switch_at_iter": 100,
            "learning_rate": 0.05
        }
    }
}

parser = argparse.ArgumentParser()
parser.add_argument("agent", choices=["KnowledgeTransfer", "AsyncKnowledgeTransfer"])
parser.add_argument("envs", type=str)
parser.add_argument("destination", type=str)

def main():
    args = parser.parse_args()
    predef["agent"]["name"] = args.agent
    predef["environments"]["source"] = args.envs
    with open(args.destination, "w") as f:
        json.dump(predef, f)

if __name__ == '__main__':
    main()
