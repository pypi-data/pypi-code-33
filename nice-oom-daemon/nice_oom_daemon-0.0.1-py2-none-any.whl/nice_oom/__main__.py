import argparse
import signal
import sys
import threading
import time

import docker
import simplejson as json


threads = {}
stop_program = [False]


def monitor_container(container, stop_signals, grace_period):
  def helper():
    soft_memory_limit = container.attrs["HostConfig"]["MemoryReservation"]
    hard_memory_limit = container.attrs["HostConfig"]["Memory"]
    if soft_memory_limit == 0:
      print ("No soft limit set for container: " + container.id[:12] + " skipping monitoring.")
      return

    print ("Monitoring container: " + container.id[:12])
    time_over_limit_condition_started = None
    print ("soft_memory_limit: {}, hard_memory_limit: {}".format(soft_memory_limit, hard_memory_limit))
    for stat in container.stats():
      if stop_program[0]: 
        return
      stats = json.loads(stat)
      if 'usage' not in stats['memory_stats']:
        return

      used_bytes = stats['memory_stats']['usage']

      if used_bytes > soft_memory_limit and time_over_limit_condition_started is None:
        print ("container {} is using more memory than it's soft limit: {}, usage: {} waiting for {} for memory use to come down.".format(
                  container.id[:12],
                  soft_memory_limit,
                  used_bytes,
                  grace_period
                  ))
        time_over_limit_condition_started = time.time()
      elif used_bytes > soft_memory_limit and time.time()  - time_over_limit_condition_started > grace_period:
        print ("container {} used too much memory, stopping it now: {}, usage: {} ".format(
          container.id[:12],
          soft_memory_limit,
          used_bytes))
        for signal, wait_time in stop_signals:
          if stop_program[0]: 
            return
          print("Sending signal " + signal)
          container.kill(signal)
          time.sleep(wait_time)
          container.reload()
          if container.status in ('removing', 'exited', 'dead'):
            print ("container {} stopped nicely, we can stop trying to kill it.".format(container.id[:12]))
            return
        print ("container {} did not stop - giving up on it.".format(container.id[:12]))
        return
      elif used_bytes < soft_memory_limit:
        time_over_limit_condition_started = None

  return helper


def halt_threads(signum, frame):
  print("Shutting down threads")
  stop_program[0] = True
  sys.exit(0)


def main():

  parser = argparse.ArgumentParser(description='Monitor docker containers and stop them when they use more memory than their soft limit.')

  parser.add_argument(
    '--stop-signal',
    nargs='+',
    required=True,
    help='Stop signals which should be sent to containers sigint=10')

  parser.add_argument(
    '--grace-period',
    default=0,
    type=int,
    help='The amount of time to wait before stopping a container once it\'s using more than their soft limit')

  args = parser.parse_args()

  client = docker.from_env()

  stop_signals = [x.split('=') for x in args.stop_signal]
  stop_signals = [(x[0], int(x[1])) for x in stop_signals]


  signal.signal(signal.SIGINT, halt_threads)
  signal.signal(signal.SIGTERM, halt_threads)


  while True:

    for container in client.containers.list():
      if container.id not in threads:          
        thread = threading.Thread(target=monitor_container(container, stop_signals, args.grace_period))
        thread.daemon = True
        threads[container.id] = {"thread": thread, "container": container}
        thread.start()

    container_ids_to_remove = []

    for container_id, state in threads.items():
      if not state['thread'].isAlive():
        state['container'].reload()
        if state['container'].status in ('removing', 'exited', 'dead'):
          container_ids_to_remove.append(container_id)

    for container_id in container_ids_to_remove:
      del threads[container_id]

    time.sleep(1)

  print(args)

if __name__ == "__main__":
    main()