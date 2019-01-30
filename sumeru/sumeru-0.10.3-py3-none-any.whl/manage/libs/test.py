from crython.tab import default_tab as tab
from crython.expression import CronExpression

def func(**kwargs):
    print (kwargs)


for i in range(1):
    task_id = i
    expr = '0 43 16 28 11 * *'

    func.ctx = 'thread'
    func.cron_expression = CronExpression.new(expr)
    func.params = {'task_id': i}

    tab.register(task_id, func)

tab.start()

print ('sleep')
import time
time.sleep(100)
