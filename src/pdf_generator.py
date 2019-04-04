#! /usr/bin/env python3
'''
This Template has a separate console and file logging.
File logging-level can be changed by -L parameter.
Log file can be changed by -l parameter.
Standard values for logging can be set in the config file
-> "Logging"
---> "logFile"
---> "logLevel"
Console logging is INFO or DEBUG according to debug debug_flag.
Config file path can be changed by -C parameter.
'''

import argparse
from common_helper_files import create_dir_for_file
import configparser
import logging
import os
import sys


PROGRAM_NAME = 'FACT PDF Report Generator'
PROGRAM_VERSION = '0.1'
PROGRAM_DESCRIPTION = 'Generates a analysis PDF report'

STANDARD_CONF_FILE = os.path.dirname(os.path.abspath(__file__)) + '/config/main.cfg'


def _setup_argparser():
    parser = argparse.ArgumentParser(description='{} - {}'.format(PROGRAM_NAME, PROGRAM_DESCRIPTION))
    parser.add_argument('-V', '--version', action='version', version='{} {}'.format(PROGRAM_NAME, PROGRAM_VERSION))
    parser.add_argument('-l', '--log_file', help='path to log file')
    parser.add_argument('-L', '--log_level', help='define the log level [DEBUG,INFO,WARNING,ERROR]')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='print debug messages')
    parser.add_argument('-C', '--config_file', help='set path to config File', default=STANDARD_CONF_FILE)
    return parser.parse_args()


def _get_console_output_level(debug_flag):
    if debug_flag:
        return logging.DEBUG
    else:
        return logging.INFO


def _setup_logging(config, debug_flag=False):
    log_level = getattr(logging, config['Logging']['logLevel'], None)
    log_format = logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    create_dir_for_file(config['Logging']['logFile'])
    file_log = logging.FileHandler(config['Logging']['logFile'])
    file_log.setLevel(log_level)
    file_log.setFormatter(log_format)
    console_log = logging.StreamHandler()
    console_log.setLevel(_get_console_output_level(debug_flag))
    console_log.setFormatter(log_format)
    logger.addHandler(file_log)
    logger.addHandler(console_log)


def _load_config(args):
    config = configparser.ConfigParser()
    config.read(args.config_file)
    if args.log_file is not None:
        config['Logging']['logFile'] = args.log_file
    if args.log_level is not None:
        config['Logging']['logLevel'] = args.log_level
    return config


if __name__ == '__main__':
    args = _setup_argparser()
    config = _load_config(args)
    _setup_logging(config, args.debug)
    logging.info(args.config_file)

    # insert your program here

    sys.exit()
