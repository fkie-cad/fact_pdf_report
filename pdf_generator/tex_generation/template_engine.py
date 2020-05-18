import logging
from base64 import decodebytes
from collections import OrderedDict
from contextlib import suppress
from pathlib import Path
from time import localtime, strftime

import jinja2
from common_helper_files import human_readable_file_size

GENERIC_TEMPLATE = 'generic.tex'
MAIN_TEMPLATE = 'main.tex'
META_TEMPLATE = 'meta.tex'
CUSTOM_TEMPLATE_CLASS = 'twentysecondcv.cls'
PLUGIN_TEMPLATE_BLUEPRINT = '{}.tex'
LOGO_FILE = 'fact.png'


def render_number_as_size(number, verbose=True):
    if not isinstance(number, (int, float)):
        return 'not available'
    if verbose:
        return '{} ({})'.format(human_readable_file_size(int(number)), format(number, ',d') + ' Byte')
    return human_readable_file_size(int(number))


def render_unix_time(unix_time_stamp):
    if not isinstance(unix_time_stamp, (int, float)):
        return 'not available'
    return strftime('%Y-%m-%d %H:%M:%S', localtime(unix_time_stamp))


def render_number_as_string(number):
    if isinstance(number, int):
        return '{:,}'.format(number)
    if isinstance(number, float):
        return '{:,.2f}'.format(number)
    if isinstance(number, str):
        with suppress(ValueError):
            return str(int(number))
    return 'not available'


def replace_special_characters(data):
    latex_character_escapes = OrderedDict()
    latex_character_escapes['\\'] = ''
    latex_character_escapes['\''] = ''
    latex_character_escapes['/'] = ' '
    latex_character_escapes['$'] = '\\$'
    latex_character_escapes['('] = '$($'
    latex_character_escapes[')'] = '$)$'
    latex_character_escapes['['] = '$[$'
    latex_character_escapes[']'] = '$]$'
    latex_character_escapes['#'] = '\\#'
    latex_character_escapes['%'] = '\\%'
    latex_character_escapes['&'] = '\\&'
    latex_character_escapes['_'] = '\\_'
    latex_character_escapes['{'] = '\\{'
    latex_character_escapes['}'] = '\\}'
    latex_character_escapes['^'] = '\\textasciicircum{}'
    latex_character_escapes['~'] = '\\textasciitilde{}'
    latex_character_escapes['>'] = '\\textgreater{}'
    latex_character_escapes['<'] = '\\textless{}'
    latex_character_escapes['\n'] = '\\newline '

    for character, replacement in latex_character_escapes.items():
        if character in data:
            data = data.replace(character, replacement)
    return data


def decode_base64_to_file(base64_string, filename, directory, suffix='png'):
    file_path = Path(directory, '{}.{}'.format(filename, suffix))
    file_path.write_bytes(decodebytes(base64_string.encode('utf-8')))
    return str(file_path)


def replace_characters_in_list(list_of_strings):
    return [
        replace_special_characters(item) for item in list_of_strings
    ]


def split_hash_string(hash_string, max_length=61):
    if len(hash_string) > max_length:
        hash_string = '{}\n{}'.format(hash_string[:max_length], hash_string[max_length:])
    return hash_string


def split_long_lines(multiline_string, max_length=92):
    def evaluate_split(line):
        return line if len(line) <= max_length else '{}\n{}'.format(line[:max_length], line[max_length:])

    return ''.join(
        evaluate_split(line) for line in multiline_string.splitlines(keepends=True)
    )


def item_contains_string(item, string):
    if not isinstance(item, str):
        return False
    return string in item


# X-Executable in summary
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


def plugin_name(name):
    return ' '.join((part.title() for part in name.split('_')))


def get_five_longest_entries(summary, top=5):
    sorted_summary = dict()
    if len(summary) < 6:
        return summary
    for key in sorted(summary, key=lambda key: len(summary[key]), reverse=True):
        sorted_summary.update({key: summary[key]})
        if len(sorted_summary) == top:
            return sorted_summary


def _add_filters_to_jinja(environment):
    environment.filters['number_format'] = render_number_as_size
    environment.filters['nice_unix_time'] = render_unix_time
    environment.filters['nice_number'] = render_number_as_string
    environment.filters['filter_chars'] = replace_special_characters
    environment.filters['elements_count'] = len
    environment.filters['base64_to_png'] = decode_base64_to_file
    environment.filters['check_list'] = lambda x: x if x else ['list is empty']
    environment.filters['plugin_name'] = plugin_name
    environment.filters['filter_list'] = replace_characters_in_list
    environment.filters['split_hash'] = split_hash_string
    environment.filters['split_output_lines'] = split_long_lines
    environment.filters['contains'] = item_contains_string
    environment.filters['top_five'] = get_five_longest_entries


class TemplateEngine:
    def __init__(self, template_folder=None, tmp_dir=None):
        self._environment = create_jinja_environment(template_folder if template_folder else 'default')
        self._tmp_dir = tmp_dir

    def render_main_template(self, analysis, meta_data):
        template = self._environment.get_template(MAIN_TEMPLATE)
        return template.render(analysis=analysis, meta_data=meta_data)

    def render_meta_template(self, meta_data):
        template = self._environment.get_template(META_TEMPLATE)
        return template.render(meta_data=meta_data)

    def render_analysis_template(self, plugin, analysis):
        try:
            template = self._environment.get_template(PLUGIN_TEMPLATE_BLUEPRINT.format(plugin))
        except jinja2.TemplateNotFound:
            logging.warning('Falling back on generic template for {}'.format(plugin))
            template = self._environment.get_template(GENERIC_TEMPLATE)
        return template.render(plugin_name=plugin, selected_analysis=analysis, tmp_dir=self._tmp_dir)

    def render_template_class(self):
        template = self._environment.get_template(CUSTOM_TEMPLATE_CLASS)
        return template.render(tmp_dir=self._tmp_dir)
