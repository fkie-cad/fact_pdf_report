import os
import shutil
import sys
from pathlib import Path

from common_helper_process import execute_shell_command_get_return_code

from pdf_generator.tex_generation.template_engine import (
    CUSTOM_TEMPLATE_CLASS, LOGO_FILE, MAIN_TEMPLATE, META_TEMPLATE, TemplateEngine
)

PDF_NAME = Path(MAIN_TEMPLATE).with_suffix('.pdf').name


def execute_latex(tmp_dir):
    current_dir = os.getcwd()
    os.chdir(tmp_dir)
    output, return_code = execute_shell_command_get_return_code('env buf_size=1000000 pdflatex {}'.format(MAIN_TEMPLATE))
    if return_code != 0:
        print(f'Error when trying to build PDF:\n{output}')
        sys.exit(1)
    os.chdir(current_dir)


def copy_fact_image(target):
    shutil.copy(str(Path(__file__).parent / 'templates' / LOGO_FILE), str(Path(target) / LOGO_FILE))


def create_report_filename(meta_data):
    unsafe_name = '{}_analysis_report.pdf'.format(meta_data['device_name'])
    safer_name = unsafe_name.replace(' ', '_').replace('/', '__')
    return safer_name.encode('latin-1', errors='ignore').decode('latin-1')


def compile_pdf(meta_data, tmp_dir):
    copy_fact_image(tmp_dir)
    execute_latex(tmp_dir)
    target_path = Path(tmp_dir, create_report_filename(meta_data))
    shutil.move(str(Path(tmp_dir, PDF_NAME)), str(target_path))
    return target_path


def create_templates(analysis, meta_data, tmp_dir, template_style='default'):
    engine = TemplateEngine(template_folder=template_style, tmp_dir=tmp_dir)
    Path(tmp_dir, MAIN_TEMPLATE).write_text(engine.render_main_template(analysis=analysis))
    Path(tmp_dir, META_TEMPLATE).write_text(engine.render_meta_template(meta_data))

    if template_style == 'default':
        Path(tmp_dir, CUSTOM_TEMPLATE_CLASS).write_text(engine.render_template_class())
