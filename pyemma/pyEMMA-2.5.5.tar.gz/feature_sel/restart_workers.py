from celery import Celery

broker_url = 'amqp://marscher:foobar@wallaby:5672/myvhost'
app = Celery('tasks', broker=broker_url)

app.control.broadcast('pool_restart')
