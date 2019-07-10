import logging
from base64 import decodebytes
from pathlib import Path
from time import localtime, strftime

import jinja2
from common_helper_files import human_readable_file_size

GENERIC_TEMPLATE = 'generic.tex'


def byte_number_filter(number, verbose=True):
    if isinstance(number, (int, float)):
        if verbose:
            return '{} ({})'.format(human_readable_file_size(int(number)), format(number, ',d') + ' bytes')
        return human_readable_file_size(int(number))
    return 'not available'


def nice_unix_time(unix_time_stamp):
    '''
    input unix_time_stamp
    output string 'YYYY-MM-DD HH:MM:SS'
    '''
    if isinstance(unix_time_stamp, (int, float)):
        tmp = localtime(unix_time_stamp)
        return strftime('%Y-%m-%d %H:%M:%S', tmp)
    return unix_time_stamp


def nice_number_filter(number):
    if isinstance(number, int):
        return '{:,}'.format(number)
    if isinstance(number, float):
        return '{:,.2f}'.format(number)
    if number is None:
        return 'not available'
    return number


def filter_latex_special_chars(data):  # pylint: disable=too-complex,too-many-branches
    if '\\' in data:
        data = data.replace('\\', '')
    if '$' in data:
        data = data.replace('$', '\\$')
    if '(' in data:
        data = data.replace('(', '$($')
    if ')' in data:
        data = data.replace(')', '$)$')
    if '[' in data:
        data = data.replace('[', '$[$')
    if ']' in data:
        data = data.replace(']', '$]$')
    if '#' in data:
        data = data.replace('#', '\\#')
    if '%' in data:
        data = data.replace('%', '\\%')
    if '&' in data:
        data = data.replace('&', '\\&')
    if '_' in data:
        data = data.replace('_', '\\_')
    if '{' in data:
        data = data.replace('{', '\\{')
    if '}' in data:
        data = data.replace('}', '\\}')
    if '^' in data:
        data = data.replace('^', '\\textasciicircum{}')
    if '~' in data:
        data = data.replace('~', '\\textasciitilde{}')
    if '>' in data:
        data = data.replace('>', '\\textgreater{}')
    if '<' in data:
        data = data.replace('<', '\\textless{}')
    if '\n' in data:
        data = data.replace('\n', '\\newline ')
    if '\'' in data:
        data = data.replace('\'', '')
    return data


def count_elements_in_list(ls):
    return len(ls)


def convert_base64_to_png_filter(base64_string, filename, directory):
    file_path = Path(directory, filename + '.png')
    file_path.write_bytes(decodebytes(base64_string.encode('utf-8')))
    return str(file_path)


def check_if_list_empty(list_of_strings):
    return list_of_strings if list_of_strings else ['list is empty']


def filter_chars_in_list(list_of_strings):
    return [
        filter_latex_special_chars(item) for item in list_of_strings
    ]


def split_hash(hash_value):
    if len(hash_value) > 61:
        hash_value = hash_value[:61] + ' ' + hash_value[61:]
    return hash_value


def split_output_lines(output_value):
    splited_lines = output_value.splitlines()
    output = ''

    for line in splited_lines:
        line_length = len(line)
        # word_lengths.append(list(map(len, line.split(' '))))
        if line_length > 92:
            line = line[:92] + ' ' + line[92:]
        output += line + '\n'
    return output


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


class Engine:
    def __init__(self, template_folder=None, tmp_dir=None):
        self._environment = create_jinja_environment(template_folder if template_folder else 'default')
        self._tmp_dir = tmp_dir

    def render_main_template(self, analysis, meta_data):
        template = self._environment.get_template('main.tex')
        return template.render(analysis=analysis, meta_data=meta_data)

    def render_meta_template(self, meta_data):
        template = self._environment.get_template('meta_data.tex')
        return template.render(meta_data=meta_data)

    def render_analysis_template(self, plugin, analysis):
        try:
            template = self._environment.get_template('{}.tex'.format(plugin))
        except jinja2.TemplateNotFound:
            logging.warning('Falling back on generic template for {}'.format(plugin))
            template = self._environment.get_template(GENERIC_TEMPLATE)
        return template.render(selected_analysis=analysis, tmp_dir=self._tmp_dir)
