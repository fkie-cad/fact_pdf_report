import logging

from jinja2 import TemplateNotFound

GENERIC_TEMPLATE = 'generic.tex'


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
    except TemplateNotFound:
        logging.debug('Falling back on generic template for {}'.format(analysis_plugin))
        template = environment.get_template(GENERIC_TEMPLATE)

    logging.debug('Rendering {}'.format(analysis_plugin))
    return template.render(selected_analysis=analysis, tmp_dir=tmp_dir)


def create_report_filename(meta_data):
    main_tex_filename = meta_data['device_name'] + '_analysis_report.pdf'
    main_tex_filename = main_tex_filename.replace(' ', '_')
    return main_tex_filename.replace('/', '__')
