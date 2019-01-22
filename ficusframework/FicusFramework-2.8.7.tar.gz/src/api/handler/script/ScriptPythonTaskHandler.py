import logging
import threading

from api.handler.ICacheAbleHandler import ICacheAbleHandler
from api.handler.ITaskHandler import ITaskHandler
from api.handler.outputer.ISimpleOutputer import ISimpleOutputer
from api.handler.script import ScriptPythonFactory
from api.model.FdInputPipe import FdInputPipe
from api.model.ResultVO import *
from client import ComputeExecutionClient, DataCrawlClient

log = logging.getLogger('Ficus')


class ScriptPythonTaskHandler(ITaskHandler,ISimpleOutputer, ICacheAbleHandler):
    """
    Python脚本的执行器
    """

    # 由于这个的实现有可能是 单例的,所以要使用ThreadLocal
    __code_local_host = threading.local()
    __execution_message_local = threading.local()

    def __init__(self, job_id, update_time, script_source):
        self.job_id = job_id
        self.update_time = update_time
        self.script_source = script_source
        self.killed = False
        self.current_task = None

    def update_time(self):
        return self.update_time

    def execute(self, params):
        """
        执行Python脚本的处理
        :param params:
        :return:
        """
        if params is None or len(params) == 0 or ("site_" not in params) or ("projectCode_" not in params) or (
                "code_" not in params):
            # 不存在ce的信息,没法执行
            return ResultVO(FAIL_CODE, "执行失败,没有找到执行器的信息")

        self.killed = False

        # 获取ce定义
        dataComputeExecution = ComputeExecutionClient.get(params["site_"], params["projectCode_"], params["code_"])

        if dataComputeExecution is None:
            # 说明有可能是crawl
            dataCrawl = DataCrawlClient.get(params["site_"], params["projectCode_"], params["code_"])
            if dataCrawl is None:
                ResultVO(FAIL_CODE, "执行失败,没有找到执行器的信息")
            return self.do_script_crawl(dataCrawl,params)

        return self.do_script_compute_execution(dataComputeExecution,params)


    def kill(self):
        self.killed = True

        if  self.current_task is not None:
            try:
                self.current_task.kill()
            except Exception as e:
                log.error(
                    f"当前正在执行的任务强制停止失败: {str(e)}")

        ScriptPythonFactory.destroy_instance(f"ScriptPython{self.job_id}")

    def is_killed(self):
        return self.killed

    def get_execution_message_cache(self):
        """
        返回message_cache
        :return:
        """
        return self.__execution_message_local.content

    def get_code_thread_local(self):
        return self.__code_local_host

    def do_script_crawl(self,dataCrawl, params):
        """
        执行动态的crawl
        :param dataCrawl:
        :param params:
        :return:
        """
        # 这里动态的加载script源文件
        simpleScriptCrawl = ScriptPythonFactory.load_instance(f"ScriptPython{self.job_id}", self.script_source,"ISimpleScriptCrawl")
        self.current_task = simpleScriptCrawl

        try:
            self.set_local_code(
                f"{dataCrawl.site}_{dataCrawl.projectCode}_{dataCrawl.code}")
            resultList = simpleScriptCrawl.do_crawl(params)
        except Exception as e:
            log.error(
                f"{dataCrawl.site}_{dataCrawl.projectCode}_{dataCrawl.code} 执行失败,{str(e)}")
            return ResultVO(FAIL_CODE,
                            f"{dataCrawl.site}_{dataCrawl.projectCode}_{dataCrawl.code} 执行失败,{str(e)}")
        finally:
            self.clear_local_code()
            self.current_task = None

        return self._send_results(params,resultList,dataCrawl.outputFdCodes)

    def do_script_compute_execution(self, dataComputeExecution, params):
        """
        执行ce的脚本
        :param dataComputeExecution:
        :param params:
        :return:
        """

        # 这里动态的加载script源文件
        simpleScriptCE = ScriptPythonFactory.load_instance(f"ScriptPython{self.job_id}",self.script_source,"ISimpleScriptCE")
        self.current_task = simpleScriptCE

        try:
            self.set_local_code(f"{dataComputeExecution.site}_{dataComputeExecution.projectCode}_{dataComputeExecution.code}")
            resultList = simpleScriptCE.do_compute(FdInputPipe(dataComputeExecution.sourceFdCodes),params)
        except Exception as e:
            log.error(f"{dataComputeExecution.site}_{dataComputeExecution.projectCode}_{dataComputeExecution.code} 执行失败,{str(e)}")
            return ResultVO(FAIL_CODE, f"{dataComputeExecution.site}_{dataComputeExecution.projectCode}_{dataComputeExecution.code} 执行失败,{str(e)}")
        finally:
            self.clear_local_code()
            self.current_task = None

        return self._send_results(params,resultList,dataComputeExecution.outputFdCodes)


    def _send_results(self,params, resultList,outputFdCodes):
        """
        发送结果数据
        :param params:
        :param resultList:
        :param outputFdCodes:
        :return:
        """
        if resultList is None or len(resultList) == 0:
            # 搞完了,没的结果,不处理
            return SUCCESS
        # 有结果,就需要从crawl的配置中找到目标的fd,然后调用fd的接口进行保存

        try:
            self.send_output_result(params["code_"], resultList, outputFdCodes)
        except Exception as e:
            log.error(
                f"{params['site_']}_{params['projectCode_']}_{params['code_']} 发送结果数据失败,{str(e)}")
        return SUCCESS