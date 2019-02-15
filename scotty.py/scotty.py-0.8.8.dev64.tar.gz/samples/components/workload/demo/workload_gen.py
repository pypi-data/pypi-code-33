import logging
import time

from scotty.utils.workload import WorkloadUtils

logger = logging.getLogger(__name__)

def run(context):
    workload = context.v1.workload
    workload_utils = WorkloadUtils(context)
    demo_resource = workload_utils.resources['demo_res']
    for i in range(0, 2):
        time.sleep(1)
    return demo_resource.endpoint['url']

def collect(context):
    workload = context.v1.workload
    workload_utils = WorkloadUtils(context)
    with workload_utils.open_file('my_result_file.txt', 'w') as f:
        f.write(f'{workload.result}\n')

def clean(context):
    pass
