from datetime import datetime


class ETL():

    def __init__(
        self,
        logger,
        learningdb_dynamodb_data_helper=None,
        learningdb_s3_data_helper=None):
        self.logger = logger
        self.learningdb_dynamodb_data_helper = learningdb_dynamodb_data_helper
        self.learningdb_s3_data_helper = learningdb_s3_data_helper

    def compute_vm_battery_count(self, dt_hour_str):
        # get vm status
        vm_status_log = self.learningdb_s3_data_helper.get_latest_vm_status(dt_hour_str)

        if len(vm_status_log)==0:
            self.logger.warn('No vm_status in %s' % dt_hour_str)
            return

        # aggregation by 10 minutes
        status = {}
        for log in vm_status_log:
            # map snap time by 10 minutes
            reg_snap_time = datetime.fromtimestamp(int(log['snap_time']))
            reg_snap_time = reg_snap_time.replace(minute=reg_snap_time.minute//10*10, second=0).timestamp()
            dt_str = self.learningdb_s3_data_helper.get_dt_str_by_timestamp(int(reg_snap_time))
            dt_minute_str = dt_str['dt_minute_str']
            vm_id = log['vm_id']
            if dt_minute_str in status:
                if vm_id in status[dt_minute_str]:
                    status[dt_minute_str][vm_id]['battery_single_count'] = max(
                        log['battery_single_count'],
                        status[dt_minute_str][vm_id]['battery_single_count'])
                    status[dt_minute_str][vm_id]['battery_pair_count'] = max(
                        log['battery_pair_count'],
                        status[dt_minute_str][vm_id]['battery_pair_count'])
                else:
                    status[dt_minute_str][vm_id] = ({
                        'battery_single_count': log['battery_single_count'],
                        'battery_pair_count': log['battery_pair_count']
                    })
            else:
                status[dt_minute_str] = {}
                status[dt_minute_str][vm_id] = {
                    'battery_single_count': log['battery_single_count'],
                    'battery_pair_count': log['battery_pair_count']
                }
        data = {}
        for dt_minute_str, status_log in status.items():
            hour_data = []
            for vm_id, log in status_log.items():
                hour_data.append({
                    'vm_id': vm_id,
                    'battery_single_count': log['battery_single_count'],
                    'battery_pair_count': log['battery_pair_count']
                })
            data[dt_minute_str] = hour_data
        # save to s3
        self.learningdb_s3_data_helper.write_vm_battery_count(data, dt_hour_str)

    def compute_vm_exchange_count(self, dt_hour_str):
        # get battery swap log
        battery_swap_log = self.learningdb_s3_data_helper.get_latest_battery_swap_log(dt_hour_str)
        
        if len(battery_swap_log)==0:
            self.logger.warn('No battery_swap_log in %s' % dt_hour_str)
            return

        vm = {}
        # parse as vm count
        for log in battery_swap_log:
            if 'vm_guid' not in log:
                continue
            vm_guid = log['vm_guid']
            if vm_guid in vm:
                vm[vm_guid]['swap_battery_count'] += len(log['swap_out'])
                vm[vm_guid]['swap_count'] += 1
            else:
                vm[vm_guid] = {
                    'swap_count': 1,
                    'swap_battery_count': len(log['swap_out'])
                }
        data = []
        for vm_guid in vm:
            data.append({
                'vm_guid': vm_guid,
                'swap_count': vm[vm_guid]['swap_count'],
                'swap_battery_count': vm[vm_guid]['swap_battery_count']
            })        

        # save to s3
        self.learningdb_s3_data_helper.write_vm_exchange_count(data, dt_hour_str)
        
