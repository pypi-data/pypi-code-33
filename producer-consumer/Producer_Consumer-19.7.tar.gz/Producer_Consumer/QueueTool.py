#!/usr/bin/env python
# _*_ coding:utf-8 _*_

"""
File:   QueueTool.py
Author: Lijiacai (lijiacai@baidu.com)
Date: 2019-02-03
Description:
    Queue producer and consumer model, including multi-process consumption queue model
"""
import json
import os
import sys
import multiprocessing
import time

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)


class QueueProducer(object):
    """producer in queue"""

    def __init__(self, queue=multiprocessing.Queue(), max_size=100, sleep_time=0.01):
        """
        init producer for Queue
        :param queue: Queue object
        :param max_size: the size of queue
        :param sleep_time: Program sleep time when the queue is full

            Note:
                producer = QueueProducer(max_size=100)    // the size of queue is 100
                producer = QueuePoducer(queue=multiprocessing.Queue(1000),max_size=100)  // the size of queue is 1000

        """
        self.sleep_time = sleep_time
        if queue == None:
            self.queue = multiprocessing.Queue(max_size)
        else:
            self.queue = queue
        try:
            self.queue.full()
        except:
            raise (IOError, "Please give a Queue")

    def produce(self, obj, block=True, timeout=None):
        """
        produce data to queue
        :param obj: data object
        :param block: Whether blocking,type is Boolean
        :param timeout: timeout
        :return:
        """
        while self.queue.full():
            time.sleep(self.sleep_time)
        if block == False:
            self.queue.put_nowait(obj)
        else:
            self.queue.put(obj, block=block, timeout=timeout)


class QueueConsumer(object):
    """consumer in queue"""

    def __init__(self, queue=None):
        """
        init consumer for queue
        :param queue: Queue object

            Note:
                queue = Queue()
                consumer = QueueConsumer(queue=queue)
        """
        self.queue = queue
        try:
            self.queue.full()
        except:
            raise (IOError, "Please give a Queue")

    def consume(self, block=True, timeout=None):
        """
        consume from queue
        :param block: Whether blocking,type is Boolean
        :param timeout: timeout
        :return:
        """
        if block == False:
            response = self.queue.get_nowait()
        else:
            response = self.queue.get(block=block, timeout=timeout)
        return response


class QueueConsumerProcess(multiprocessing.Process):
    """Consumer multiprocessing process"""

    def __init__(self, target=None, input_queue=multiprocessing.Queue(), batch_size=100,
                 delimiter="\n", filename="", filemode="a", lock=None,
                 group=None, name=None,
                 args=tuple(), kwargs=None):
        """
        Initialize the consumer multiprocess module
        :param target: Data processing function. It must be function object.
        :param input_queue: queue object
        :param batch_size: batch data to file, such as 100 groups of data  // batch_size=100
        :param delimiter: A separator between data such as "\n"
        :param filename: If you need to write data to file.
        :param filemode: the file mode , such as "a", "w", "ab" and so on
        :param lock: Lock object , if you need to write data to file, you should give a Lock() object
        :param group: the group of multiprocessing.Process
        :param name: Process name
        :param args: Parameters to the target object, You must give a tuple object, such as args=()
        :param kwargs: the kwargs of multiprocessing.Process

            Note:
            p_list = []
            for i in range(5):
                p = QueueConsumerProcess(target=func,args=(data2,data3),filename="test.json")
                p.start()
                p_list.append(p)
            for i in p_list:
                p.stop()
                p.join()

        """
        self.args = args if args else ()
        self.kwargs = kwargs if kwargs else {}
        super(QueueConsumerProcess, self).__init__(group=group, name=name, args=(), kwargs={})
        self.input_queue = input_queue
        self.target = target
        self.batch_size = batch_size
        self.queueconsumer = QueueConsumer(queue=self.input_queue)
        self.stop_consumer_value = multiprocessing.Manager().Value("b", False)
        self.batch_list = []
        self.delimiter = delimiter
        self.filename = filename
        self.filemode = filemode
        self.lock = lock
        if self.filename and not self.lock:
            raise (TypeError, "lock object must be Lock, just like multiprocessing.Lock()")

    def run(self):
        """run"""
        self.consumer()

    def consumer(self):
        """consumer"""
        while not self.stop_consumer_value.value:
            try:
                data = self.queueconsumer.consume(block=False)
            except Exception as e:
                continue
            if self.target:
                result = self.target(data, *self.args, **self.kwargs)
                if result == None:
                    continue
                if self.filename:
                    if not type(result) == str and not type(result) == unicode:
                        raise (TypeError, "The character type we expect is a string")
                    self.batch_list.append(result)
                    if len(self.batch_list) > self.batch_size:
                        batch_string = self.delimiter.join(self.batch_list) + self.delimiter
                        self.batch_list = []
                        self.lock.acquire()
                        with open(self.filename, self.filemode, 0) as f:
                            f.write(batch_string)
                        self.lock.release()
            else:
                result = self.func(data=data)
        if self.filename:
            batch_string = self.delimiter.join(self.batch_list) + self.delimiter
            self.batch_list = []
            self.lock.acquire()
            with open(self.filename, self.filemode, 0) as f:
                f.write(batch_string)
            self.lock.release()

    def stop(self):
        while not self.input_queue.empty():
            pass
        self.stop_consumer_value.value = True

    def func(self, data):
        # print(data)
        pass


def test_func(data):
    """test function"""
    return json.dumps({"result": data})


def test():
    """test"""
    process_list = []
    producer = QueueProducer()
    lock = multiprocessing.Lock()
    # start consumer
    for i in range(4):
        p = QueueConsumerProcess(target=test_func, input_queue=producer.queue, filename="123.json",
                                 name="process%d" % i, lock=lock)
        p.start()
        process_list.append(p)

    # start producer
    for i in range(1000000):
        producer.produce(str(i))

    print "produce done"
    # wait for child process
    for p in process_list:
        p.stop()
        p.join()


if __name__ == '__main__':
    test()

