import sys
sys.path.insert(0, '/home/jonas/Nextcloud/Programmieren/PyCharm/statepub')

import time
import math
import click

from statepub.state import ComputingState
from statepub.publish import StatePublisher, FullStatePublisher


"""
CHANGELOG

Added 27.12.2018

Changed 24.01.2019
"""


@click.command(name='publish-status', short_help='Publish the status of this machine to the MQTT network')
@click.option('--interval', default=2, help='Amount of seconds between two publishes')
@click.option('--broker_port', default=1883, help='The port on which the MQTT broker operates')
@click.argument('broker_ip', metavar='<broker ip>')
@click.argument('topic', metavar='<topic>')
def cli(interval, broker_port, broker_ip, topic):
    """
    After invoking this command, it will repeatedly after set intervals sent the status of this machine to the MQTT
    network
    """
    click.echo('Starting to publish status to broker at "{}::{}"'.format(broker_ip, broker_port))
    click.echo('Starting with the interval "{}"'.format(interval))

    publisher = FullStatePublisher(topic, broker_ip, broker_port=broker_port)

    # 24.01.2019
    # Added a new loop on the outside, which is going to retry the whole code, in case the There was en error
    while True:
        try:

            computing_state = ComputingState()
            time_seconds_before = 0
            while True:
                timestamp = time.time()
                time_seconds = math.ceil(timestamp)
                if (time_seconds - 1) % interval == 0 and time_seconds_before != time_seconds:
                    time_seconds_before = time_seconds
                    # Actually execute the relevant code for the publishing here
                    publisher.full_publish(('computation', computing_state), timestamp=timestamp)

                time.sleep(0.01)

        except OSError:
            click.echo('Couldnt connect to broker')
            # Retrying after a minute.
            time.sleep(60)

        except KeyboardInterrupt:
            publisher.close()
            # Breaking the outer loop, because a KeyboardInterrupt means the user really wants to stop the program
            click.echo('\n')
            exit()


if __name__ == '__main__':
    cli()
