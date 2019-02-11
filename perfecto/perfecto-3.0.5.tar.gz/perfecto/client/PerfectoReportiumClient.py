from constants import *
from PerfectoDeprecator import deprecated


class PerfectoReportiumClient:
    """
    Perfecto Reporting client
    """
    def __init__(self, perfecto_execution_context):
        """
        initialize a new reporting client
        :param perfecto_execution_context:
        """
        self.perfecto_execution_context = perfecto_execution_context
        self.webdriver = perfecto_execution_context.webdriver
        self.started = False

    def test_start(self, name, context):
        """
        inform reporting system about new test execution
        :param name: test name
        :param context: a context instance contains array of string tags
        :return: ---
        """
        params = {}
        job = self.perfecto_execution_context.job
        project = self.perfecto_execution_context.project
        test_tags = self.perfecto_execution_context.context_tags
        cFields = self.perfecto_execution_context.customFields
		

        if job is not None:
            params['jobName'] = job.name
            params['jobNumber'] = job.number
            params['jobBranch'] = job.branch

        if project is not None:
            params['projectName'] = project.name
            params['projectVersion'] = project.version

        params['name'] = name
        allTags = list(context.tags)

        if test_tags is not None:
            allTags.extend(test_tags)

        params['tags'] = allTags
	
        if (len(context.customFields) > 0):
            cFields.update(context.customFields)
		
        """
        Need to convert the Custom fields into a string parameter
        where each Custom Field is in the form <key>=<value>
        """
        str_cFields = []
        for key, val in cFields.items():
            cFieldS = key + '=' + val 
            str_cFields.append(cFieldS)

        params['customFields'] = str_cFields
        self.execute_script(START_TEST_COMMAND, params)
        self.started = True

    @deprecated('Consider to use step_start and step_end commands instead')
    def test_step(self, description):
        """
        ### Deprecated call use step_start instead ###
        inform reporting system about a new test step
        :param description:
        :return:
        """
        params = {'name': description}
        self.execute_script(START_STEP_COMMAND, params)

    def step_start(self, description):
        """
        inform reporting system about a new test step
        :param description:
        :return:
        """
        params = {'name': description}
        self.execute_script(START_STEP_COMMAND, params)

    def step_end(self, message=None):
        """
        inform reporting system about an end of a test step
        :param message:
        :return:
        """
        params = {'message': message}
        self.execute_script(END_STEP_COMMAND, params)


    def test_stop(self, test_result,context=None):
        """
        inform reporting system about an end of test execution
        :param test_result:
        :return:
        """

        if not self.started:
            return False
        params = {'success': test_result.is_successful()}

        if test_result.is_successful() is False:
            params['failureDescription'] = test_result.get_message()
            params['failureReason'] = test_result.get_failureReason()
        if context != None: #if there is no context skip to the end
            if context.tags is not None:
                allTags = list(context.tags)
                params['tags'] = allTags

            if (len(context.customFields) > 0):
                cFields = context.customFields
                """
                Need to convert the Custom fields into a string parameter
                where each Custom Field is in the form <key>=<value>
                """
                str_cFields = []
                for key, val in cFields.items():
                    cFieldS = key + '=' + val
                    str_cFields.append(cFieldS)

                params['customFields'] = str_cFields
        self.execute_script(END_TEST_COMMAND, params)
        return True

    def reportium_assert(self, message, status):
        """
        reportium assertion
        :param message:
        :param status:
        :return:
        """
        params = {
            'message': message,
            'status': status
        }

        self.execute_script(ASSERT_COMMAND, params)

    def report_url(self):
        """
        retrieve the report url
        :return: report's url
        """
        url = ''
        if hasattr(self.webdriver, 'capabilities'):
            url = str(self.webdriver.capabilities[executionReportUrl])
        else:
            raise 'WebDriver instance is assumed to have Selenium Capabilities'
        return url

    def execute_script(self, script, params):
        """
        Using WebDriver instance in order to execute command against reporting system
        :param script: string representation of the command to be executed
        :param params: commands parameters
        :return: command's return value
        """
        return self.webdriver.execute_script(script, params)
