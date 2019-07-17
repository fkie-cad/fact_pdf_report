import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from common_helper_process import execute_shell_command
from pdf_generator.pre_processing.rest import create_request_url, request_firmware_data
from pdf_generator.tex_generation.template_engine import Engine


def execute_latex(tmp_dir):
    current_dir = os.getcwd()
    os.chdir(tmp_dir)
    execute_shell_command('env buf_size=1000000 pdflatex main.tex')
    os.chdir(current_dir)


def copy_fact_image(target):
    shutil.copy(str(Path(__file__).parent / 'templates' / 'fact_logo.png'), str(Path(target) / 'fact_logo.png'))


def generate_analysis_templates(engine, analysis):
    return [
        ('{}.tex'.format(analysis_plugin), engine.render_analysis_template(analysis_plugin, analysis[analysis_plugin])) for analysis_plugin in analysis
    ]


def create_report_filename(meta_data):
    unsafe_name = '{}_analysis_report.pdf'.format(meta_data['device_name'])
    safer_name = unsafe_name.replace(' ', '_').replace('/', '__')
    return safer_name.encode('latin-1', errors='ignore').decode('latin-1')


def compile_pdf(meta_data, tmp_dir):
    copy_fact_image(tmp_dir)
    execute_latex(tmp_dir)
    target_path = Path(tmp_dir, create_report_filename(meta_data))
    shutil.move(str(Path(tmp_dir, 'main.pdf')), str(target_path))
    return target_path


def create_templates(analysis, meta_data, tmp_dir):
    engine = Engine(tmp_dir=tmp_dir)

    Path(tmp_dir, 'main.tex').write_text(engine.render_main_template(analysis=analysis, meta_data=meta_data))
    Path(tmp_dir, 'meta.tex').write_text(engine.render_meta_template(meta_data))
    for filename, result_code in generate_analysis_templates(engine=engine, analysis=analysis):
        Path(tmp_dir, filename).write_text(result_code)


def generate_report(firmware_uid, server_url=None):
    request_url = create_request_url(firmware_uid, server_url)
    try:
        analysis, meta_data = request_firmware_data(request_url)
    except RuntimeError as error:
        logging.warning('No firmware found with UID {}: {}'.format(firmware_uid, error))
        return 1

    with TemporaryDirectory() as tmp_dir:
        create_templates(analysis, meta_data, tmp_dir)
        compile_pdf(meta_data, tmp_dir)

    return 0
