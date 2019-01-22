etl_s3_root_dir = 'ml/etl-workspace'
etl_local_root_dir = 'tmpdata/etl-workspace'

etl_battery_swap_log = {
    'key': 'battery-swap-log'
}

etl_vm_exchange_count = {
    'key': 'vm-exchange-count'
}


class ETLPathHelper():

    def __init__(self):
        self.s3_root_dir = 'ml/etl-workspace'
        self.local_root_dir = 'tmpdata/etl-workspace'

    def get_etl_key(self, etl_name):
        return {
            'battery_swap_log': 'battery-swap-log',
            'vm_battery_count': 'vm-battery-count',
            'vm_exchange_count': 'vm-exchange-count',
            'vm_status': 'vm-status'
        }[etl_name]

    def get_battery_swap_log_dirs(self, dt_hour_str, update_time_str=''):
        etl_key = self.get_etl_key('battery_swap_log')
        return self.get_dirs_by_etl_key(etl_key, dt_hour_str, update_time_str=update_time_str)

    def get_vm_battery_count_dirs(self, dt_hour_str, update_time_str=''):
        etl_key = self.get_etl_key('vm_battery_count')
        return self.get_dirs_by_etl_key(etl_key, dt_hour_str, update_time_str=update_time_str)

    def get_vm_exchange_count_dirs(self, dt_hour_str, update_time_str=''):
        etl_key = self.get_etl_key('vm_exchange_count')
        return self.get_dirs_by_etl_key(etl_key, dt_hour_str, update_time_str=update_time_str)
    
    def get_vm_status_dirs(self, dt_hour_str, update_time_str=''):
        etl_key = self.get_etl_key('vm_status')
        return self.get_dirs_by_etl_key(etl_key, dt_hour_str, update_time_str=update_time_str)

    def get_dirs_by_etl_key(self, etl_key, dt_hour_str, update_time_str=''):
        path = {}
        path['s3folder'] = '%s/%s/%s/%s' % (self.s3_root_dir, etl_key, dt_hour_str, update_time_str)
        path['local_dir'] = '%s/%s/%s/%s' % (self.local_root_dir, etl_key, dt_hour_str, update_time_str)
        path['s3prefix'] = '%s/%s/%s' % (self.s3_root_dir, etl_key, dt_hour_str)
        path['local_prefix'] = '%s/%s/%s' % (self.local_root_dir, etl_key, dt_hour_str)
        return path


def get_local_battery_swap_log_dir(dt_hour_str, update_time_str):
    return '%s/%s/%s/%s' % (etl_local_root_dir, etl_battery_swap_log['key'], dt_hour_str, update_time_str)

def get_battery_swap_log_dir(dt_hour_str, update_time_str):
    return '%s/%s/%s/%s' % (etl_s3_root_dir, etl_battery_swap_log['key'], dt_hour_str, update_time_str)

def get_local_etl_vm_exchange_count_dir(dt_hour_str, update_time_str):
    return '%s/%s/%s/%s' % (etl_local_root_dir, etl_vm_exchange_count['key'], dt_hour_str, update_time_str)

def get_etl_vm_exchange_count_dir(dt_hour_str, update_time_str):
    return '%s/%s/%s/%s' % (etl_s3_root_dir, etl_vm_exchange_count['key'], dt_hour_str, update_time_str)

def get_local_battery_swap_log_prefix(dt_hour_str):
    return '%s/%s/%s' % (etl_local_root_dir, etl_battery_swap_log['key'], dt_hour_str)

def get_battery_swap_log_prefix(dt_hour_str):
    return '%s/%s/%s' % (etl_s3_root_dir, etl_battery_swap_log['key'], dt_hour_str)

def get_local_etl_vm_exchange_count_prefix(dt_hour_str):
    return '%s/%s/%s' % (etl_local_root_dir, etl_vm_exchange_count['key'], dt_hour_str)

def get_etl_vm_exchange_count_prefix(dt_hour_str):
    return '%s/%s/%s' % (etl_s3_root_dir, etl_vm_exchange_count['key'], dt_hour_str)



class JobPathHelper():

    def __init__(self):
        self.s3_root_dir = 'ml/job-workspace'
        self.local_root_dir = 'tmpdata/job-workspace'

    def get_job_key(self, job_name):
        return {
            'demand_prediction': 'demand-prediction',
        }[job_name]

    def get_demand_prediction_dirs(self, update_time_str=''):
        job_key = self.get_job_key('demand_prediction')
        path = {}
        path['s3folder'] = '%s/%s/%s' % (self.s3_root_dir, job_key, update_time_str)
        path['local_dir'] = '%s/%s/%s' % (self.local_root_dir, job_key, update_time_str)
        path['s3prefix'] = '%s/%s' % (self.s3_root_dir, job_key)
        path['local_prefix'] = '%s/%s' % (self.local_root_dir, job_key)
        return path


