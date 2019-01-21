import random
import threading
import datetime


class Instance:

    def __init__(self, num_instances):
        self.instances = {}
        self.max_instance = num_instances
        self.gc = threading.Timer(5 * 60, self.__garbage_collector)  # 5 min
        self.gc.start()

    def get(self):
        num = 0

        if len(self.instances) >= self.max_instance:
            # log_hdle.warn('-1', 'instance quota exceeded')
            return -1

        while num < self.max_instance:
            num += 1
            inst = random.randint(1, self.max_instance)
            if inst not in self.instances:
                self.instances[inst] = _InstObj(inst, {})
                return self.instances[inst]
        return None

    def release(self, instance):
        if instance.inst_num in self.instances.keys():
            instance.clear()
            self.instances.pop(instance.inst_num)

    def list(self):
        return self.instances

    def __garbage_collector(self):
        self.gc = threading.Timer(5 * 60, self.__garbage_collector)  # 5 min
        self.gc.start()
        now = datetime.datetime.utcnow()

        if not bool(self.instances):
            return
        # Freeze list of values to protect of RuntimeError: dictionary changed size during iteration
        for ins in list(self.instances.values()):
            if ins:
                delta = now - ins.get_created()
                if delta.seconds > 10 * 60:  # 10 min
                    self.release(ins)


class _InstObj:
    def __init__(self, inst_num, objs):
        self.inst_num = inst_num
        self.objs = objs
        self.created_at = datetime.datetime.utcnow()

    def add_obj(self, ref, obj):
        self.objs.update({ref: obj})

    def add_db(self, hdle):
        self.add_obj('db_cnx', hdle)

    def add_log(self, hdle):
        self.add_obj('log', hdle)

    def add_sendmail(self, hdle):
        self.add_obj('sendmail', hdle)

    def get_obj(self, ref):
        return self.objs.get(ref, None)

    def get_logger_hdle(self):
        return self.get_obj('log')

    def get_db_hdle(self):
        return self.get_obj('db_cnx')

    def get_sendmail_hdle(self):
        return self.get_obj('sendmail')

    def get_created(self):
        return self.created_at

    def get_ins(self):
        return self.inst_num

    def clear(self):
        self.objs.clear()
