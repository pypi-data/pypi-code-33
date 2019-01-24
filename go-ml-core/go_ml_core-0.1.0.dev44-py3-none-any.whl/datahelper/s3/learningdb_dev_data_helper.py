from datahelper.s3.s3_data_helper import S3DataHelper
from datahelper.s3.ml_learning_dev import s3_path_helper as S3PathHelper
from datahelper.s3.ml_learning_dev.s3_path_helper import ETLPathHelper, JobPathHelper 
from datetime import datetime
import json
import os

class DataHelper(S3DataHelper):

    def __init__(
        self, 
        logger=None,
        config_file='go_servers.ini',
        host_name='ML_Learning_DEV'):
        super().__init__( 
            logger=logger,
            config_file=config_file,
            host_name=host_name)

    def connect(self):
        super().connect()

    #####################################################
    #
    #   jobs
    #
    #####################################################

    def filter_by_time(self, keys, filter_time_str):
        filter_keys = []
        for key in keys:
            time_str = key.split('/')[-2]
            if datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S') <= datetime.strptime(filter_time_str, '%Y-%m-%dT%H:%M:%S'):
                filter_keys.append(key)
        return filter_keys

    def get_latest_job_s3key(self, job_keys):
        if len(job_keys)==0:
            return None
        job_keys.sort(key=lambda x:x, reverse=True)
        for i in range(0, len(job_keys)):
            # if (Not _SUCCESS file) and (have corresponding _SUCCESS file)
            s3key = job_keys[i]
            s3_success_key = '%s%s' % ('/'.join(s3key.split('/')[:-1]), '/_SUCCESS')
            if s3key[-8:]!='_SUCCESS' and s3_success_key in job_keys:
                return s3key

        return None 

    def get_demand_prediction_result_s3folder(self, update_time_str=''):
        job_path = JobPathHelper().get_demand_prediction_dirs()
        job_prefix = job_path['s3prefix']
        job_keys = self.get_keys(job_prefix)
        if len(job_keys)==0:
            return None
        if update_time_str!='':
            job_keys = self.filter_by_time(job_keys, update_time_str)
        s3path = self.get_latest_job_s3key(job_keys)
        # return a folder 
        s3folder = s3path[:s3path.rfind('/')]
        update_time_str = s3folder.split('/')[-1]
        self.logger.info('get demand_prediction_result s3folder = %s' % s3folder)
        return [s3folder, update_time_str]

    def download_demand_prediction_result(self, update_time_str=''):
        [s3folder, update_time_str] = self.get_demand_prediction_result_s3folder(update_time_str=update_time_str)
        if s3folder is None:
            self.logger.warn('No demand_prediction_result before %s', update_time_str)
            return []

        job_path = JobPathHelper().get_demand_prediction_dirs(update_time_str=update_time_str)
        #print(job_path)
        
        self.download_folder(s3folder, job_path['local_dir'])

        return job_path['local_dir']

    def upload_demand_prediction_result(self, update_time_str=''):
        if update_time_str=='':
            update_time_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        job_path = JobPathHelper().get_demand_prediction_dirs(update_time_str=update_time_str)
    
        # upload
        self.upload_folder(job_path['s3folder'], job_path['local_dir'])

    #####################################################
    #
    #   etl
    #
    #####################################################

    def get_latest_etl_s3key(self, etl_objs):
        if len(etl_objs)==0:
            return None

        etl_objs.sort(key=lambda x:x['Key'], reverse=True)
        keys = [x['Key'] for x in etl_objs]
        for i in range(0, len(etl_objs)):
            # if (Not _SUCCESS file) and (have corresponding _SUCCESS file)
            s3key = etl_objs[i]['Key']
            s3_success_key = '%s%s' % ('/'.join(s3key.split('/')[:-1]), '/_SUCCESS')
            if s3key[-8:]!='_SUCCESS' and s3_success_key in keys:
                return s3key

        return None

    #####################################################
    # Vm Status
    #####################################################

    def get_latest_vm_status_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_vm_status_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_objs = self.list_object(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_objs)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest battery_swap_log')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest vm_status s3folder = %s' % s3folder)
            return s3folder

    def get_latest_vm_status(self, dt_hour_str):
        s3folder = self.get_latest_vm_status_s3folder(dt_hour_str)
        if s3folder is None:
            self.logger.warn('No latest_vm_status in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_vm_status_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data.extend(json_data['data'])

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_status in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_status[0] = %s' % data[0])
        return data

    def write_vm_status(self, item_dict_list):
        if (len(item_dict_list))==0:
            self.logger.warn('Empty input of vm status')
            return
        # data preprocessing
        dict_dt_hour = {}
        for item_dict in item_dict_list:
            [_, dt_hour_str, _] = self.timestamp_to_dt_str(item_dict['snap_time'])
            if dt_hour_str in dict_dt_hour:
                dict_dt_hour[dt_hour_str].append(item_dict)
            else:
                dict_dt_hour[dt_hour_str] = [item_dict]

        # upload data to s3
        [dt_now_str, _, _] = self.timestamp_to_dt_str(int(datetime.now().timestamp()))
        for dt_hour_str, item_list in dict_dt_hour.items():
            etl_path = ETLPathHelper().get_vm_status_dirs(dt_hour_str, update_time_str=dt_now_str)

            # write local file and upload
            self.mkdir(etl_path['local_dir'])
            json_data = {}
            json_data['data'] = item_list
            with open('%s/%s.json' % (etl_path['local_dir'], dt_now_str), 'w') as fp:
                json.dump(json_data, fp)
            # upload
            self.upload_folder(etl_path['s3folder'], etl_path['local_dir'])
            # remove local file
            self.rmdir(etl_path['local_dir'])   

    #####################################################
    # general sync table (by Vm-Hour)
    #####################################################

    def get_latest_battery_swap_log_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_battery_swap_log_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_objs = self.list_object(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_objs)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest battery_swap_log')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest battery_swap_log s3folder = %s' % s3folder)
            return s3folder

    def get_latest_battery_swap_log(self, dt_hour_str):
        s3folder = self.get_latest_battery_swap_log_s3folder(dt_hour_str)
        if s3folder is None:
            self.logger.warn('No latest_battery_swap_log in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_battery_swap_log_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from battery_swap_log in %s' % (len(data), dt_hour_str))
        self.logger.info('battery_swap_log[0] = %s' % data[0])
        return data

    def write_battery_swap_log(self, item_dict_list):
        if (len(item_dict_list))==0:
            self.logger.warn('Empty input of battey swap log')
            return
        # data preprocessing
        dict_dt_hour = {}
        for item_dict in item_dict_list:
            [_, dt_hour_str, _] = self.timestamp_to_dt_str(item_dict['exchange_time'])
            if dt_hour_str in dict_dt_hour:
                dict_dt_hour[dt_hour_str].append(item_dict)
            else:
                dict_dt_hour[dt_hour_str] = [item_dict]
        
        # upload data to s3
        #[dt_now_str, _, _] = self.timestamp_to_dt_str(int(datetime.now().timestamp()))
        for dt_hour_str, item_list in dict_dt_hour.items():
            etl_key = ETLPathHelper().get_etl_key('battery_swap_log')
            self.write_etl_data(item_list, dt_hour_str, etl_key)
            # s3folder = S3PathHelper.get_battery_swap_log_dir(dt_hour_str, dt_now_str)
            # local_dir = S3PathHelper.get_local_battery_swap_log_dir(dt_hour_str, dt_now_str)
            # # write local file and upload
            # self.mkdir(local_dir)
            # json_data = {}
            # json_data['data'] = item_list
            # with open('%s/%s.json' % (local_dir, dt_now_str), 'w') as fp:
            #     json.dump(json_data, fp)
            # # upload
            # self.upload_folder(s3folder, local_dir)
            # # remove local file
            # self.rmdir(local_dir)

    #####################################################
    # general etl (by Vm-Hour)
    #####################################################

    def get_latest_vm_battery_count_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_vm_battery_count_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_objs = self.list_object(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_objs)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest battery_swap_log')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest vm_battery_count s3folder = %s' % s3folder)
            return s3folder

    def get_latest_vm_exchange_count_s3folder(self, dt_hour_str):
        job_path = ETLPathHelper().get_vm_exchange_count_dirs(dt_hour_str)
        job_prefix = job_path['s3prefix']
        etl_objs = self.list_object(job_prefix)
        s3path = self.get_latest_etl_s3key(etl_objs)
        # return a folder 
        if s3path == None:
            self.logger.warn('No latest battery_swap_log')
            return None
        else:
            s3folder = '/'.join(s3path.split('/')[:-1])
            self.logger.info('get latest vm_exchange_count s3folder = %s' % s3folder)
            return s3folder
    
    def get_latest_vm_battery_count(self, dt_hour_str):
        s3folder = self.get_latest_vm_battery_count_s3folder(dt_hour_str)

        if s3folder is None:
            self.logger.warn('No latest_vm_battery_count in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_vm_battery_count_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])
        
        # read local files
        files = os.listdir(job_path['local_dir'])
        data = None
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_battery_count in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_battery_count.keys() = %s' % list(data.keys()))
        return data 

    def get_latest_vm_exchange_count(self, dt_hour_str):
        s3folder = self.get_latest_vm_exchange_count_s3folder(dt_hour_str)

        if s3folder is None:
            self.logger.warn('No latest_vm_exchange_count in %s', dt_hour_str)
            return []

        job_path = ETLPathHelper().get_vm_exchange_count_dirs(
            dt_hour_str, 
            update_time_str=s3folder.split('/')[-1])

        self.download_folder(job_path['s3folder'], job_path['local_dir'])

        # read local files
        files = os.listdir(job_path['local_dir'])
        data = []
        for file in files:
            if file[-5:] != '.json':
                continue
            path = '%s/%s' % (job_path['local_dir'], file)
            with open(path) as fp:
                json_data = json.load(fp)
                data = json_data['data']

        # remove local files
        self.rmdir(job_path['local_dir'])

        self.logger.info('Read %s logs from vm_exchange_count in %s' % (len(data), dt_hour_str))
        self.logger.info('vm_exchange_count[0] = %s' % data[0])
        return data 

    def write_vm_battery_count(self, data, dt_hour_str):
        etl_key = ETLPathHelper().get_etl_key('vm_battery_count')
        self.write_etl_data(data, dt_hour_str, etl_key)
        # dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        # etl_path = ETLPathHelper().get_vm_battery_count_dirs(dt_hour_str, update_time_str=dt_now_str)
		# # write local file and upload
        # self.mkdir(etl_path['local_dir'])
        # json_data = {}
        # json_data['data'] = data
        # with open('%s/%s.json' % (etl_path['local_dir'], dt_now_str), 'w') as fp:
        #     json.dump(json_data, fp)
        # # upload
        # self.upload_folder(etl_path['s3folder'], etl_path['local_dir'])
        # # remove local file
        # self.rmdir(etl_path['local_dir'])

    def write_vm_exchange_count(self, data, dt_hour_str):
        etl_key = ETLPathHelper().get_etl_key('vm_exchange_count')
        self.write_etl_data(data, dt_hour_str, etl_key)
        # dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        # etl_path = ETLPathHelper().get_vm_exchange_count_dirs(dt_hour_str, update_time_str=dt_now_str)
		# # write local file and upload
        # self.mkdir(etl_path['local_dir'])
        # json_data = {}
        # json_data['data'] = data
        # with open('%s/%s.json' % (etl_path['local_dir'], dt_now_str), 'w') as fp:
        #     json.dump(json_data, fp)
        # # upload
        # self.upload_folder(etl_path['s3folder'], etl_path['local_dir'])
        # # remove local file
        # self.rmdir(local_dir)

    def write_etl_data(self, data, dt_hour_str, etl_key):
        dt_now_str = self.get_dt_str_by_timestamp(int(datetime.now().timestamp()))['dt']
        etl_path = ETLPathHelper().get_dirs_by_etl_key(etl_key, dt_hour_str, update_time_str=dt_now_str)
        # write local file and upload
        self.mkdir(etl_path['local_dir'])
        json_data = {}
        json_data['data'] = data
        with open('%s/%s.json' % (etl_path['local_dir'], dt_now_str), 'w') as fp:
            json.dump(json_data, fp)
        # upload
        self.upload_folder(etl_path['s3folder'], etl_path['local_dir'])
        # remove local file
        self.rmdir(etl_path['local_dir'])

    
    #####################################################
    #
    #   general
    #
    #####################################################

    def timestamp_to_dt_str(self, timestamp):
        '''
        Return a date_string and time_string by given timestamp
        '''
        dt_str = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
        dt_hour_str = dt_str[:13]
        time_str = dt_str[-8:]
        return [dt_str, dt_hour_str, time_str]

    def get_dt_str_by_timestamp(self, timestamp):
        '''
        Return a string format dict by given timestamp
        '''
        dt_str = {}
        dt_str['dt'] = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
        dt_str['dt_hour_str'] = dt_str['dt'][:13]
        dt_str['dt_minute_str'] = dt_str['dt'][:16]
        dt_str['time_str'] = dt_str['dt'][-8:]
        return dt_str

    
