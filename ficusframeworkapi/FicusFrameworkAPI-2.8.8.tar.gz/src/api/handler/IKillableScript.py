
class IKillableScript:

    def kill(self):
        """
        杀掉任务
        :return:
        """
        pass

    def is_killed(self)->bool:
        """
        判断是否杀掉了
        :return:
        """
        return False