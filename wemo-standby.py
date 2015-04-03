#!/usr/bin/env python

import argparse
import sys
import logging
import time

from ouimeaux.environment import Environment
from ouimeaux.utils import matcher
from ouimeaux.signals import receiver, statechange, devicefound


def _get_args():
    """Get arguments and options."""
    parser = argparse.ArgumentParser(description='wemo-standby',
                                     prog='wemo-standby.py')

    parser.add_argument('-l', '--log-level',
                        dest='log', action='store', default="warning",
                        metavar="LOG LEVEL",
                        help='Set the log level. (Default: %(default)s)')
    parser.add_argument('--log-file',
                        dest='log_file', action='store', default=None,
                        metavar="LOG_FILE",
                        help='Set the log file.')

    args = parser.parse_args()
    return args


def mainloop(name):
    matches = matcher(name)

    def is_standby(name):
        print "Waiting for standby or powerof"
        switch = env.get_switch(name)
        time.sleep(10)
        normal_power = switch.current_power
        time.sleep(10)

        while switch.get_state():
            if switch.current_power < (normal_power * 0.2):
                print "Device in standby mode!"
                break
            time.sleep(10)

    @receiver(devicefound)
    def found(sender, **kwargs):
        if matches(sender.name):
            print "Found device:", sender.name

    @receiver(statechange)
    def on_off(sender, **kwargs):
        if matches(sender.name):
            print "{} state is {state}".format(
                sender.name, state="on" if kwargs.get('state') else "off")
            if kwargs.get('state'):
                is_standby(sender.name)

    env = Environment(with_cache=False)
    try:
        env.start()
        env.discover(10)
        env.wait()
    except (KeyboardInterrupt, SystemExit):
        print "Goodbye!"
        sys.exit(0)

def main():

    args = _get_args()
    # Setup Logging
    numeric_log_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_log_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=numeric_log_level,
                        format='[%(asctime)s %(levelname)s] %(message)s',
                        datefmt='%Y%m%d %H:%M:%S',
                        filename=args.log_file)

    logging.info("[wemo-standby] Starting up...")

    # Start
    mainloop('WeMo Insight')
    # End
    logging.info("[wemo-standby] Shutting down ...")

if __name__ == '__main__':
    main()

