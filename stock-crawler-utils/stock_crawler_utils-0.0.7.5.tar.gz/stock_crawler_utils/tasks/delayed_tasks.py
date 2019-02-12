import pika
import pickle


def delay_task_queue(ttl_delay, queue, channel, task):
    exchange = "exchange_delay_task"
    channel.exchange_declare(
        exchange=exchange, type="x-delayed-message",
        arguments={"x-delayed-type": "direct"}
    )
    channel.queue_bind(
        queue=queue, exchange=exchange, routing_key=queue
    )
    channel.basic_publish(
        exchange=exchange, routing_key=queue,
        body=pickle.dumps(task), properties=pika.BasicProperties(
            delivery_mode=2, headers={"x-delay": ttl_delay}
        )
    )