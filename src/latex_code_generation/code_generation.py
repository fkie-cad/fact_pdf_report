import jinja2
import logging
import argparse
import os
from pathlib import Path
from src.rest_import.rest import *
# from web_interface.filter import byte_number_filter, nice_unix_time, nice_number_filter
from src.jinja_filters.filter import *


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


def _setup_jinja_filters():
    jinja_env = _set_jinja_env()
    # jinja_env.filters['number_format'] = byte_number_filter
    jinja_env.filters['nice_unix_time'] = nice_unix_time
    jinja_env.filters['nice_number'] = nice_number_filter
    jinja_env.filters['filter_chars'] = filter_latex_special_chars
    jinja_env.filters['elements_count'] = count_elements_in_list
    jinja_env.filters['base64_to_png'] = convert_base64_to_png_filter
    jinja_env.filters['check_list'] = check_if_list_empty
    jinja_env.filters['split_hash'] = split_hash
    jinja_env.filters['split_output_lines'] = split_output_lines


def generate_code(analysis_dict, output_path):
    jinja_env = _set_jinja_env()
    _render_template(analysis_dict, jinja_env, 'meta_data')


def _render_template(data, jinja_env, template):
    output = jinja_env.get_template('{}.tex'.format(template))
    return output.render(analysis=data['analysis'], meta_data=data['meta_data'])


def _create_tex_files(analysis_dict, jinja_env):
    module_list = list(analysis_dict['analysis'].keys())
    module_list.append('meta_data')
    for module in module_list:
        try:
            _render_template(analysis_dict, jinja_env, module)
        except Exception as e:
            logging.error('Could not generate tex file: {} -> {}'.format(type(Exception), e))


def _write_file(raw_data, file_path):
    with open(file_path, 'w') as fp:
        fp.write(raw_data)


def create_pdf_report(meta_data):
    main_tex_filename = meta_data['device_name'] + "_Analysis_Report.tex"
    main_tex_filename = main_tex_filename.replace(" ", "_")
    main_tex_filename = main_tex_filename.replace("/", "__")
    os.system("env buf_size=1000000 pdflatex " + main_tex_filename)


def delete_unnecessary_files():
    dir = "./"
    dir_content = os.listdir(dir)

    for file in dir_content:
        if file.endswith(".tex"):
            os.remove(os.path.join(dir, file))
        elif file.endswith(".log"):
            os.remove(os.path.join(dir, file))
        elif file.endswith(".aux"):
            os.remove(os.path.join(dir, file))
        elif os.path.splitext(os.path.basename(file))[0] == "entropy_analysis_graph":
            os.remove(os.path.join(dir, "entropy_analysis_graph.png"))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description='PDF Genearator for the Firmware Analysis and Comparison Tool (FACT)')
    argparser.add_argument('-s', '--summaries', default=False, help='Create a PDF report including summaries', dest="summary", action="store_false")
    argparser.add_argument('-uid', '--uid', help='firmware analysis UID', dest="uid")

    args = argparser.parse_args()
    '''
    if args.verbose:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
    '''
    # request_url = create_request_url(args.uid)
    request_url = create_request_url()
    firmware_dict = get_firmware(request_url)
    firmware_meta_data = get_firmware_meta_data(firmware_dict)
    firmware_analyses = get_firmware_analyses(firmware_dict)

    _set_jinja_env()
    _setup_jinja_filters()
    # create_pdf_report(firmware_meta_data)
    delete_unnecessary_files()
    '''
    if args.summary:
        pass

    else:

        setup_jinja_filters()
        create_main_tex(meta_data, analysis)
        create_meta_tex(meta_data)
        create_analysis_texs_with_summary(analysis)
        create_pdf_report(meta_data)
        delete_generated_files()
        print("Analysis report generated successfully.")
    '''