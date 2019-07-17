#!/usr/bin/env python3
'''
    fact_pdf_report
    Copyright (C) 2015-2019  Fraunhofer FKIE

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse
import logging
import sys

from common_helper_files import create_dir_for_file
from pdf_generator.generator import generate_report

PROGRAM_NAME = 'FACT PDF Report Generator'
PROGRAM_VERSION = '0.1'
PROGRAM_DESCRIPTION = 'Generates an analysis PDF report'


def setup_argparser():
    parser = argparse.ArgumentParser(description='{} - {}'.format(PROGRAM_NAME, PROGRAM_DESCRIPTION))
    parser.add_argument('-V', '--version', action='version', version='{} {}'.format(PROGRAM_NAME, PROGRAM_VERSION))
    parser.add_argument('-l', '--log_file', help='path to log file')
    parser.add_argument('-L', '--log_level', help='define the log level [DEBUG,INFO,WARNING,ERROR]')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='print debug messages')
    parser.add_argument('UID', help='firmware analysis UID')
    return parser.parse_args()


def setup_logging(debug_flag=False):
    log_format = logging.Formatter(fmt='[%(asctime)s][%(module)s][%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    create_dir_for_file('/tmp/pdf_generator.log')
    file_log = logging.FileHandler('/tmp/pdf_generator.log')
    file_log.setLevel(logging.INFO)
    file_log.setFormatter(log_format)
    logger.addHandler(file_log)

    console_log = logging.StreamHandler()
    console_log.setLevel(logging.DEBUG if debug_flag else logging.INFO)
    console_log.setFormatter(log_format)
    logger.addHandler(console_log)


if __name__ == '__main__':
    ARGS = setup_argparser()
    setup_logging(ARGS.debug)
    sys.exit(generate_report(ARGS.UID))
