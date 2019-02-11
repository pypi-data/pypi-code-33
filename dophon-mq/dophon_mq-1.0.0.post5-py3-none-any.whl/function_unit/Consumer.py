import inspect
from dophon_mq.utils import *
from dophon_mq import function_unit

center = function_unit.center


def consumer(tag: str, delay: int = 0, arg_name: str = 'args'):

    def method(f):
        tags = tag if isinstance(tag, list) else tag.split('|')
        def queue_args(*args, **kwargs):
            @join_threadable
            def do_consume(tt):
                center.write_p_book(tt)
                try:
                    center.do_get(p_name=tt, delay=delay, f=f, kwargs=kwargs, arg_name=arg_name)
                except Exception as e:
                    print(e)

            for t in tags:
                if arg_name in inspect.getfullargspec(f).kwonlyargs:
                    # 执行消息中心信息监听
                    do_consume(t)
                elif arg_name in inspect.getfullargspec(f).args:
                    do_consume(t)
                else:
                    print('%s方法不存在参数: %s' % (str(f), arg_name))


        if len(tags) > 1 and properties.msg_queue_debug:
            print('监听多个标签', tags)

        return queue_args

    return method
