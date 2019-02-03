#!/usr/bin/env python3
import argparse
from time import sleep
from urbantz import Delivery
from urbantz.exceptions import APIError
from requests.exceptions import HTTPError


def main():
    parser = argparse.ArgumentParser(
        description="Simple UrbanTZ delivery tracker",
    )
    parser.add_argument(
        'delivery',
        type=Delivery,
        metavar='ID',
        help='A unique UrbanTZ delivery ID',
    )
    parser.add_argument(
        '-f', '--frequency',
        type=int,
        default=10,
        help='Update frequency in seconds',
    )
    options = vars(parser.parse_args())
    delivery = options['delivery']

    while True:
        try:
            delivery.update()
        except (APIError, HTTPError) as e:
            if isinstance(e, APIError) and e.code == 1:
                raise SystemExit('Invalid delivery ID')
            print('Error while fetching data:', str(e))

        distance = delivery.position.distance(delivery.destination.coordinates)
        print("{} {} meters".format(
            delivery.last_updated.isoformat(),
            round(distance, 1),
        ))
        sleep(options['frequency'])


if __name__ == '__main__':
    main()
