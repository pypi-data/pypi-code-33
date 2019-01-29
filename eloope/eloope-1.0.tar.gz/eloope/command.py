from redis import Redis
import sys


class Command:
    host = 'localhost'
    port = 6379

    @staticmethod
    def status():
        redis = Redis(Command.host, Command.port, decode_responses=True)
        pipe = redis.pipeline()
        managers = redis.keys('manager-*')
        for manager in managers:
            pipe.hgetall(manager)
        results = pipe.execute()
        return results

    @staticmethod
    def start():
        redis = Redis(Command.host, Command.port)
        redis.set('is_run', 1)
        return 'Successfully start!'

    @staticmethod
    def stop():
        redis = Redis(Command.host, Command.port)
        redis.set('is_run', -1)
        redis.flushall()
        return 'Successfully stop!'

    @staticmethod
    def help():
        return """
            status --- View the Managers status.
            start --- Start running.
            stop --- Stop running.
        """

    @staticmethod
    def command(cmd):
        command_set = {
            'status': Command.status,
            'start': Command.start,
            'stop': Command.stop,
            'help': Command.help,
        }
        return command_set[cmd]() if cmd in command_set else None


def main():
    result = Command.command(sys.argv[1])
    if result:
        print(result)
    else:
        raise Exception('The command does not exist. Please enter "help" to view the command.')
