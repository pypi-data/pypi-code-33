# encoding='utf-8'
import importlib
import sys
import time
from multiprocessing import Process
from haf.apihelper import Request, Response
from haf.asserthelper import AssertHelper
from haf.bench import HttpApiBench, BaseBench
from haf.busclient import BusClient
from haf.common.database import SQLConfig
from haf.common.exception import FailRunnerException
from haf.common.log import Log
from haf.config import *
from haf.case import HttpApiCase, BaseCase, PyCase
from haf.mark import locker
from haf.result import HttpApiResult
from haf.utils import Utils
import traceback

logger = Log.getLogger(__name__)


class Runner(Process):
    def __init__(self, log_dir: str, bus_client: BusClient):
        super().__init__()
        self.daemon = True
        self.bus_client = bus_client
        self.benchs = {}
        self.bench = None
        self.key = ""
        self.runner_key = ""
        self.lock = False
        self.runner = {"get": 0, "skip": 0, "run": {}, "done":[], "key": 0}
        self.log_dir = log_dir

    def load(self):
        pass

    def init_runner(self, case:BaseCase):
        self.bench = self.get_bench(case)

    def get_bench(self, case:BaseCase):
        bench = self.benchs.get(case.bench_name, None)
        if bench is None :
            bench = HttpApiBench()
        bench.add_case(case)
        self.benchs[case.bench_name] = bench
        return bench

    @locker
    def put_result(self,  key:str, result:HttpApiResult):
        logger.info(f"{self.key} : runner {self.pid} put result {result.case.ids.id}.{result.case.ids.subid}.{result.case.ids.name}")
        self.result_handler_queue.put(result)

    @locker
    def put_web_message(self, key:str):
        if self.web_queue.full():
            self.web_queue.get()
            self.web_queue.put(self.runner)

    @locker
    def put_case_back(self, key:str, case):
        logger.info(f"{self.runner_key} : runner put case {case.ids.id}.{case.ids.subid}-{case.ids.name}")
        self.case_handler_queue.put(case)

    def result_handler(self, result):
        if isinstance(result, HttpApiResult):
            if result.case.run == CASE_SKIP:
                self.runner["skip"] += 1
            self.runner["run"] = {}
            self.runner["done"].append({
                f"{result.case.ids.id}.{result.case.ids.subid}-{result.case.ids.name}":
                {
                    "bench_name" : result.case.bench_name,
                    "begin" : result.begin_time,
                    "end" : result.end_time,
                    "result" : RESULT_GROUP.get(str(result.result))
                }
            })
        elif isinstance(result, HttpApiCase):
            self.runner["run"] = {
                f"{result.ids.id}.{result.ids.subid}-{result.ids.name}":
                {
                    "bench_name":result.bench_name
                }
            }

        # logger.info(f"{self.key} : runner {self.pid} -- put web message {self.runner}")
        self.put_web_message("web")

    def run(self):
        try:
            #self.bus_client = BusClient()
            self.runner_key = f"{self.pid}$%runner$%"
            self.runner["key"] = f"{self.pid}"
            logger.info(f"{self.runner_key} start runner")
            self.web_queue = self.bus_client.get_publish_runner()
            self.case_handler_queue = self.bus_client.get_case()
            self.result_handler_queue = self.bus_client.get_result()
            while True:
                if not self.case_handler_queue.empty() :
                    case = self.case_handler_queue.get()
                    if case == SIGNAL_CASE_END:
                        self.end_handler()
                        break
                    result = self.run_case(case)
                    if isinstance(result, HttpApiResult):
                        self.put_result("result", result)
                time.sleep(0.1)
        except Exception as e:
            logger.error(e)
            raise FailRunnerException

    def run_case(self, local_case:HttpApiCase):
        result = HttpApiResult()
        try:
            try:
                self.key = local_case.log_key
                logger.info(f"{self.key} : runner {self.pid} -- get {local_case.ids.id}.{local_case.ids.subid}-{local_case.ids.name}")
                self.result_handler(local_case)
                self.init_runner(local_case)
                if local_case.type == CASE_TYPE_HTTPAPI:
                    api_runner = ApiRunner(self.bench)
                    result = api_runner.run(local_case)
                elif local_case.type == CASE_TYPE_PY:
                    py_runner = PyRunner(self.bench)
                    result = py_runner.run(local_case)

                if isinstance(result, list):
                    if result[0] == CASE_CAN_NOT_RUN_HERE:
                        self.put_case_back("case", local_case)
                        return
                    if result[0] == CASE_SKIP:
                        result = result[1]
                result.log_dir = f"{self.log_dir}/{local_case.bench_name}/{local_case.ids.id}.{local_case.ids.subid}.{local_case.ids.name}.log"
                result.bind_runner(self.pid)
                self.result_handler(result)
                return result
            except Exception as runerror:
                logger.error(runerror)
                result.run_error = traceback.format_exc()
                result.result = RESULT_ERROR
                return result
        except Exception as e:
            logger.error(e)
            result.run_error = traceback.format_exc()
            result.result = RESULT_ERROR
            return result

    def end_handler(self):
        logger.info("{} : end runner".format(self.runner_key))
        self.result_handler_queue.put(SIGNAL_RESULT_END)
        self.case_handler_queue.put(SIGNAL_CASE_END)


class BaseRunner(object):
    def __init__(self, bench:BaseBench):
        self.bench = bench

    def check_case_run_here(self, case):
        if len(case.dependent) == 0:
            return True
        try:
            for dependence in case.dependent:
                if dependence not in self.bench.cases.keys():
                    return False

            return True
        except Exception:
            return False

    def check_case_run(self, case): # if skip, return False
        return case.run == CASE_RUN

    def check_case_error(self, case):
        return case.error == CASE_ERROR

    def get_dependence_case_from_bench(self, dependence):
        return None


class PyRunner(BaseRunner):
    def __init__(self, bench):
        super().__init__(bench)
        self.bench = bench
        self.key = ""

    def run(self, case:PyCase):
        result = HttpApiResult()
        self.key = case.log_key
        result.on_case_begin()
        if not self.check_case_run(case): # not False is skip
            result.case = case
            result.on_case_end()
            result.result = RESULT_SKIP
            return [CASE_SKIP, result]

        result.case = case
        logger.info(f"{case.log_key} : PyRunner run - {case.bench_name} {case.ids.id}.{case.ids.subid}-{case.ids.name}")
        try:
            module_name = case.module_name
            module_path = case.module_path
            sys.path.append(module_path)
            module = importlib.import_module(module_name)
            suite = getattr(module, case.suite)()
            func = getattr(suite, case.func)
            case.request = getattr(suite, "request", Request())
            if case.param is not None:
                func(case.param)
            else:
                func()
            case.response = getattr(suite, "response", Response())
            result.result = RESULT_PASS
        except AssertionError as ae:
            traceback.print_exc()
            logger.error(ae)
            result.result = RESULT_FAIL
            result.run_error = traceback.format_exc()
            result.on_case_end()
            return result
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
            result.result = RESULT_ERROR
            result.run_error = traceback.format_exc()
            result.on_case_end()
            return result

        result.on_case_end()
        return result


class ApiRunner(BaseRunner):
    '''
    ApiRunner
    '''
    def __init__(self, bench:HttpApiBench):
        super().__init__(bench)
        self.bench = bench
        self.key = ""

    def run(self, case:HttpApiCase):
        '''
        run the HttpApiCase
        :param case: HttpApiCase
        :return: result: HttpApiResult
        '''
        self.key = case.log_key
        result = HttpApiResult()
        result.on_case_begin()
        if not self.check_case_run_here(case) :
            result.on_case_end()
            return [CASE_CAN_NOT_RUN_HERE, result]
        if not self.check_case_run(case): # not False is skip
            result.case = case
            result.on_case_end()
            result.result = RESULT_SKIP
            return [CASE_SKIP, result]

        logger.info(f"{case.log_key} : ApiRunner run - {case.ids.id}.{case.ids.subid}-{case.ids.name}")
        try:
            result.case = case
            case.response = self.request(case.request)
            result.result_check_response = self.check_response(case.response, case.expect.response)
            case.expect.sql_response_result = self.sql_response(case.sqlinfo.scripts["sql_response"], case.sqlinfo.config, case.sqlinfo.check_list["sql_response"])
            temp_r = self.check_sql_response(case)
            result.result_check_sql_response = temp_r[0]
            if not temp_r[0]:
                result.run_error = temp_r[1]
            result.case = case
            result.result = RESULT_PASS if False not in result.result_check_response and result.result_check_sql_response is True else RESULT_FAIL
        except Exception as e:
            result.run_error = e
            result.result = RESULT_ERROR
        result.on_case_end()
        return result

    def request(self, request:Request):
        return Utils.http_request(request, key=self.key)

    def sql_response(self, sql_script:str, sql_config:SQLConfig, check_list:list):
        if sql_config is None or sql_script is None:
            return None

        if check_list is None:
            sql_result = Utils.sql_execute(sql_config, sql_script, dictcursor=True, key=self.key)
        else:
            sql_result = Utils.sql_execute(sql_config, sql_script, key=self.key)
        return sql_result

    def check_response(self, response:Response, response_expect:Response):
        result = True
        result_check_code = result and AssertHelper.assert_that(response.code, 200, key=self.key)
        if response_expect.body == {}:
            result_check_body = True
        else:
            result_check_body = AssertHelper.assert_that(response.body, response_expect.body, key=self.key)
        return [result_check_code, result_check_body]

    def check_sql_response(self, case:HttpApiCase):
        '''
        check sql == response, use case's third function
        :param case:
        :return:
        '''
        try:
            result = [True, "ok"]
            if case.expect.sql_check_func is None or case.expect.sql_response_result is None:
                return [True, "ok"]
            data = case.response.body
            logger.info(f"{case.log_key} : check sql response : {case.expect.sql_check_func}")
            class_content = importlib.import_module(case.expect.sql_check_func[0])
            check_func = getattr(getattr(class_content, case.expect.sql_check_func[1]), case.expect.sql_check_func[2])
            logger.info(f"{case.log_key} : check func : {check_func}")
            logger.info(f"{case.log_key} : check list is {case.sqlinfo.check_list}")
            if case.sqlinfo.check_list is not None:
                check_func(case.expect.sql_response_result, data, case.sqlinfo.check_list["sql_response"])
            else:
                check_func(case.expect.sql_response_result, data)
        except Exception as e:
            traceback.print_exc()
            return [False, traceback.format_exc()]
        return result

