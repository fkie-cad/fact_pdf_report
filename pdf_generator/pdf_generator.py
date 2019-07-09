#! /usr/bin/env python3

import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from common_helper_files import create_dir_for_file
from common_helper_process import execute_shell_command_get_return_code
from pdf_generator.pre_processing.rest import create_request_url, request_firmware_data
from pdf_generator.tex_generation.template_engine import create_jinja_environment

PROGRAM_NAME = 'FACT PDF Report Generator'
PROGRAM_VERSION = '0.1'
PROGRAM_DESCRIPTION = 'Generates an analysis PDF report'


def setup_argparser():
    parser = argparse.ArgumentParser(description='{} - {}'.format(PROGRAM_NAME, PROGRAM_DESCRIPTION))
    parser.add_argument('-V', '--version', action='version', version='{} {}'.format(PROGRAM_NAME, PROGRAM_VERSION))
    parser.add_argument('-l', '--log_file', help='path to log file')
    parser.add_argument('-L', '--log_level', help='define the log level [DEBUG,INFO,WARNING,ERROR]')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='print debug messages')
    parser.add_argument('-u', '--uid', help='firmware analysis UID', dest="UID")
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


def execute_pdflatex(tmp_dir):
    current_dir = os.getcwd()
    os.chdir(tmp_dir)
    logging.debug('Creating pdf file')
    _, _ = execute_shell_command_get_return_code('env buf_size=1000000 pdflatex main.tex')
    os.chdir(current_dir)


def _copy_fact_image(target):
    shutil.copy(str(Path(__file__).parent.parent / 'templates' / 'fact_logo.png'), str(Path(target) / 'fact_logo.png'))


def main(firmware_uid):
    request_url = create_request_url(firmware_uid)
    try:
        firmware_analyses, firmware_meta_data = request_firmware_data(request_url)
    except KeyError:
        logging.warning('No firmware found with UID {}'.format(firmware_uid))
        return None

    environment = create_jinja_environment()

    with TemporaryDirectory() as tmp_dir:
        Path(tmp_dir, 'meta.tex').write_text(generate_meta_data_code(environment=environment, meta_data=firmware_meta_data))

        for filename, result_code in generate_analysis_codes(environment=environment, analysis=firmware_analyses, tmp_dir=tmp_dir):
            Path(tmp_dir, filename).write_text(result_code)

        Path(tmp_dir, 'main.tex').write_text(generate_main_code(firmware_analyses, firmware_meta_data, environment))

        _copy_fact_image(tmp_dir)

        execute_pdflatex(tmp_dir)

        pdf_filename = create_report_filename(firmware_meta_data)
        shutil.move(str(Path(tmp_dir, 'main.pdf')), str(Path('.', pdf_filename)))

    return None


if __name__ == '__main__':
    args = setup_argparser()
    setup_logging(args.debug)

    main(args.UID)

    sys.exit(0)
