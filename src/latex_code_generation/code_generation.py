import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import jinja2

from common_helper_process import execute_shell_command_get_return_code

from jinja_filters.filter import (
    nice_unix_time, nice_number_filter, filter_latex_special_chars, count_elements_in_list,
    convert_base64_to_png_filter, check_if_list_empty, split_hash, split_output_lines, byte_number_filter
)
from rest_import.rest import create_request_url, request_firmware_data

GENERIC_TEMPLATE = 'generic.tex'


def _set_jinja_env(templates_to_use='default'):
    template_directory = Path(Path(__file__).parent.parent, 'templates', templates_to_use)
    return jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(str(template_directory))
    )


def _setup_jinja_filters(environment):
    environment.filters['number_format'] = byte_number_filter
    environment.filters['nice_unix_time'] = nice_unix_time
    environment.filters['nice_number'] = nice_number_filter
    environment.filters['filter_chars'] = filter_latex_special_chars
    environment.filters['elements_count'] = count_elements_in_list
    environment.filters['base64_to_png'] = convert_base64_to_png_filter
    environment.filters['check_list'] = check_if_list_empty
    environment.filters['split_hash'] = split_hash
    environment.filters['split_output_lines'] = split_output_lines


def generate_meta_data_code(environment, meta_data):
    template = environment.get_template('meta_data.tex')
    return template.render(meta_data=meta_data)


def generate_main_code(firmware_analyses, firmware_meta_data, jinja_environment):
    template = jinja_environment.get_template('main.tex')
    return template.render(analysis=firmware_analyses, meta_data=firmware_meta_data)


def generate_analysis_codes(environment, analysis):
    return [
        ('{}.tex'.format(analysis_plugin), _render_analysis_result(analysis[analysis_plugin], environment, analysis_plugin)) for analysis_plugin in analysis
    ]


def _render_analysis_result(analysis, environment, analysis_plugin):
    try:
        template = environment.get_template('{}.tex'.format(analysis_plugin))
    except jinja2.TemplateNotFound:
        logging.debug('Falling back on generic template for {}'.format(analysis_plugin))
        template = environment.get_template(GENERIC_TEMPLATE)

    return template.render(selected_analysis=analysis)


def _create_tex_files(analysis_dict, jinja_env):
    module_list = list(analysis_dict['analysis'].keys())
    module_list.append('meta_data')
    for module in module_list:
        try:
            _render_analysis_result(analysis_dict, jinja_env, module)
        except Exception as e:
            logging.error('Could not generate tex file: {} -> {}'.format(type(Exception), e))


def create_report_filename(meta_data):
    main_tex_filename = meta_data['device_name'] + "_analysis_report.pdf"
    main_tex_filename = main_tex_filename.replace(" ", "_")
    return main_tex_filename.replace("/", "__")


def _copy_fact_image(target):
    shutil.copy(Path(__file__).parent.parent / 'templates' / 'fact_logo.png', Path(target) / 'fact_logo.png')


def execute_pdflatex(tmp_dir):
    current_dir = os.getcwd()
    os.chdir(tmp_dir)
    output, return_code = execute_shell_command_get_return_code('env buf_size=1000000 pdflatex main.tex')
    os.chdir(current_dir)


def generate_pdf_report(firmware_uid="bab8d95fc42176abc9126393b6035e4012ebccc82c91e521b91d3bcba4832756_3801088"
                                     ""):
    request_url = create_request_url(firmware_uid)
    firmware_analyses, firmware_meta_data = request_firmware_data(request_url)

    jinja_environment = _set_jinja_env()
    _setup_jinja_filters(environment=jinja_environment)

    with TemporaryDirectory() as tmp_dir:
        Path(tmp_dir, 'meta.tex').write_text(generate_meta_data_code(environment=jinja_environment, meta_data=firmware_meta_data))

        for filename, result_code in generate_analysis_codes(environment=jinja_environment, analysis=firmware_analyses):
            Path(tmp_dir, filename).write_text(result_code)

        Path(tmp_dir, 'main.tex').write_text(generate_main_code(firmware_analyses, firmware_meta_data, jinja_environment))

        _copy_fact_image(tmp_dir)

        execute_pdflatex(tmp_dir)

        pdf_filename = create_report_filename(firmware_meta_data)
        shutil.move(Path(tmp_dir, 'main.pdf'), Path('.', pdf_filename))
