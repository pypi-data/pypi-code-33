
class TableSyncer():

    def __init__(
        self,
        logger,
        goserver_data_helper=None,
        learningdb_dynamodb_data_helper=None,
        learningdb_s3_data_helper=None,
        dataplatform_data_helper=None):
        self.logger = logger
        self.goserver_data_helper = goserver_data_helper
        self.learningdb_dynamodb_data_helper = learningdb_dynamodb_data_helper
        self.learningdb_s3_data_helper = learningdb_s3_data_helper
        self.dataplatform_data_helper = dataplatform_data_helper

    def sync_battery_swap_log(
        self,
        start_ts,
        end_ts = 0):
        self.logger.info('Start sync_battery_swap_log.')

        # 1: Check params
        max_ts_interval = 24 * 60 * 60 
        if end_ts==0:
            end_ts = start_ts + max_ts_interval
        if end_ts > start_ts + max_ts_interval:
            end_ts = start_ts + max_ts_interval
            self.logger.warn('end_ts may not larger than start_ts+%s' % max_ts_interval)

        # 2: Get Battery Swap Log from Data Platform (Mongo)
        battery_swap_log = self.dataplatform_data_helper.get_battery_swap_log(
            start_ts=start_ts,
            end_ts=end_ts)
        
        # 3: Update Battery Swap Log to Learning Database (S3) 
        self.learningdb_s3_data_helper.write_battery_swap_log(battery_swap_log)

        self.logger.info('Finish sync_battery_swap_log.')

    def sync_vm_status(
        self,
        start_ts,
        end_ts = 0):

        self.logger.info('Start sync_vm_status.')
        
        # 1: Check params
        [start_ts, end_ts] = self.get_valid_ts(start_ts, end_ts)

        # 2: Get Vm Status from Data Platform (Mongo)
        # TODO: should use get_vm_status
        vm_status = self.dataplatform_data_helper.get_vm_status_b(
            start_ts=start_ts,
            end_ts=end_ts)

        # 3: Update Vm Status to Learning Database (S3) 
        self.learningdb_s3_data_helper.write_vm_status(vm_status)

        self.logger.info('Finish sync_vm_status.')

    
    def get_valid_ts(
        self,
        start_ts,
        end_ts = 0):
        '''
        check time interval < max_ts_interval (1 day)
        '''

        max_ts_interval = 24 * 60 * 60 
        if end_ts==0:
            end_ts = start_ts + max_ts_interval
        if end_ts > start_ts + max_ts_interval:
            end_ts = start_ts + max_ts_interval
            self.logger.warn('end_ts may not larger than start_ts+%s' % max_ts_interval)

        return [start_ts, end_ts]

    
