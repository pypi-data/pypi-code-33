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
    def run():
        redis = Redis(Command.host, Command.port)
        redis.set('is_run', 1)
        return 'Run successful!'

    @staticmethod
    def stop():
        redis = Redis(Command.host, Command.port)
        redis.set('is_run', -1)
        return 'stop successful!'

    @staticmethod
    def clear():
        redis = Redis(Command.host, Command.port)
        redis.flushall()
        return 'clear successful!'

    @staticmethod
    def help():
        return """
            run  --- Start running.
            status --- View the Managers status.
            clear  --- Clear Redis.
            stop   --- Stop running.
        """

    @staticmethod
    def command(cmd):
        command_set = {
            'run': Command.run,
            'status': Command.status,
            'clear': Command.clear,
            'stop': Command.stop,
            'help': Command.help,
        }
        return command_set[cmd]()


def main():
    try:
        params = sys.argv
        if params == 3:
            Command.host, Command.port = params[2].split(':')
        result = Command.command(params[1])
    except KeyError:
        raise Exception('The command does not exist. Please enter "help" to view the command.')
    except IndexError:
        result = Command.help()
    print(result)
