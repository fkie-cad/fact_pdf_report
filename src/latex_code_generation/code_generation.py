import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import jinja2
from common_helper_process import execute_shell_command_get_return_code
from jinja_filters.filter import (
    byte_number_filter, check_if_list_empty, convert_base64_to_png_filter, count_elements_in_list, filter_chars_in_list,
    filter_latex_special_chars, nice_number_filter, nice_unix_time, split_hash, split_output_lines
)
from rest_import.rest import create_request_url, request_firmware_data

GENERIC_TEMPLATE = 'generic.tex'


def create_jinja_environment(templates_to_use='default'):
    template_directory = Path(Path(__file__).parent.parent, 'templates', templates_to_use)
    environment = jinja2.Environment(
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(str(template_directory))
    )
    _add_filters_to_jinja(environment)
    return environment


def _add_filters_to_jinja(environment):
    environment.filters['number_format'] = byte_number_filter
    environment.filters['nice_unix_time'] = nice_unix_time
    environment.filters['nice_number'] = nice_number_filter
    environment.filters['filter_chars'] = filter_latex_special_chars
    environment.filters['elements_count'] = count_elements_in_list
    environment.filters['base64_to_png'] = convert_base64_to_png_filter
    environment.filters['check_list'] = check_if_list_empty
    environment.filters['filter_list'] = filter_chars_in_list
    environment.filters['split_hash'] = split_hash
    environment.filters['split_output_lines'] = split_output_lines


def generate_meta_data_code(environment, meta_data):
    template = environment.get_template('meta_data.tex')
    logging.debug('Rendering meta data')
    return template.render(meta_data=meta_data)


def generate_main_code(firmware_analyses, firmware_meta_data, jinja_environment):
    template = jinja_environment.get_template('main.tex')
    logging.debug('Rendering main page')
    return template.render(analysis=firmware_analyses, meta_data=firmware_meta_data)


def generate_analysis_codes(environment, analysis, tmp_dir):
    return [
        ('{}.tex'.format(analysis_plugin), _render_analysis_result(analysis[analysis_plugin], environment, analysis_plugin, tmp_dir)) for analysis_plugin in analysis
    ]


def _render_analysis_result(analysis, environment, analysis_plugin, tmp_dir):
    try:
        template = environment.get_template('{}.tex'.format(analysis_plugin))
    except jinja2.TemplateNotFound:
        logging.debug('Falling back on generic template for {}'.format(analysis_plugin))
        template = environment.get_template(GENERIC_TEMPLATE)

    logging.debug('Rendering {}'.format(analysis_plugin))
    return template.render(selected_analysis=analysis, tmp_dir=tmp_dir)


def create_report_filename(meta_data):
    main_tex_filename = meta_data['device_name'] + '_analysis_report.pdf'
    main_tex_filename = main_tex_filename.replace(' ', '_')
    return main_tex_filename.replace('/', '__')


def _copy_fact_image(target):
    shutil.copy(Path(__file__).parent.parent / 'templates' / 'fact_logo.png', Path(target) / 'fact_logo.png')


def execute_pdflatex(tmp_dir):
    current_dir = os.getcwd()
    os.chdir(tmp_dir)
    logging.debug('Creating pdf file')
    _, _ = execute_shell_command_get_return_code('env buf_size=1000000 pdflatex main.tex')
    os.chdir(current_dir)


def generate_pdf_report(firmware_uid):
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
        shutil.move(Path(tmp_dir, 'main.pdf'), Path('.', pdf_filename))

    return None
