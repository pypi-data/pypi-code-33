from google.cloud import logging
from google.cloud.logging.resource import Resource


class Logger(object):

	def create_logger(self, project_id):
		log_client = logging.Client()
		log_name = "appengine.googleapis.com%2Fgae_app"
		logger = log_client.logger(log_name.format(project_id))

		return logger

	def __init__(self, run_id, project_id, module_id, version_id):
		self.trace_id = run_id
		self.project_id = project_id
		self.module_id = module_id
		self.version_id = version_id
		self.res = Resource(type="gae_app",
				   labels={
					   "project_id": self.project_id,
					   "module_id": self.module_id,
					   "version_id": self.version_id,
				   })
		self.logger = self.create_logger(self.project_id)

	def info(self, message):
		self.logger.log_struct({'message': message, 'trace_id': self.trace_id}, resource=self.res, severity='INFO')

	def warning(self, message):
		self.logger.log_struct({'message': message, 'trace_id': self.trace_id}, resource=self.res, severity='WARNING')

	def error(self, message):
		self.logger.log_struct({'message': message, 'trace_id': self.trace_id}, resource=self.res, severity='ERROR')

	def critical(self, message):
		self.logger.log_struct({'message': message, 'trace_id': self.trace_id}, resource=self.res, severity='CRITICAL')

	def debug(self, message):
		self.logger.log_struct({'message': message, 'trace_id': self.trace_id}, resource=self.res, severity='DEBUG')
