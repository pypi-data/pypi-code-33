#!/usr/bin/env python
# _*_ coding:utf-8 _*_


"""
File: __init__.py
Author: Lijiacai
Date: 2019-02-03
Description:
    e.g1:
	from Producer_Consumer.QueueTool import QueueProducer
	from Producer_Consumer.QueueTool import QueueConsumer
	from Producer_Consumer.QueueTool import QueueConsumerProcess
	import multiprocessing
	import json


	def test_func(data):
    
    	    return json.dumps({"result": data})


	def test():
    
    	    process_list = []
            producer = QueueProducer()
    	    lock = multiprocessing.Lock()

	    # Multiprocess consumption
    	    for i in range(4):
            	p = QueueConsumerProcess(target=test_func, input_queue=producer.queue, filename="123.json",
                                 name="process%d" % i, lock=lock)
            	p.start()
            	process_list.append(p)
	    # start produce
    	    for i in range(1000000):
        	producer.produce(str(i))

    	    print "produce done"
	    # wait for child process

    	    for p in process_list:
        	p.stop()
        	p.join()

	if __name__ == '__main__':
    	    test()





"""
