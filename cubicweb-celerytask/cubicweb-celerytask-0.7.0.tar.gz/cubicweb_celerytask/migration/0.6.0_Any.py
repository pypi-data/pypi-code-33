from cubicweb_celerytask.migration.utils import migrate_task_logs_to_bfss
option_added('celerytask-log-dir')
migrate_task_logs_to_bfss(cnx)
drop_attribute('CeleryTask', 'task_logs')
