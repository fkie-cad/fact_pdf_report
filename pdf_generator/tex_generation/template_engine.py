from base64 import decodebytes
from collections import OrderedDict
from pathlib import Path
from time import localtime, strftime

from random import choice
import socket
import jinja2
from common_helper_files import human_readable_file_size

MAIN_TEMPLATE = 'main.tex'
META_TEMPLATE = 'meta.tex'
CUSTOM_TEMPLATE_CLASS = 'twentysecondcv.cls'
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


def replace_special_characters(data):
    latex_character_escapes = OrderedDict()
    latex_character_escapes['\\'] = ''
    latex_character_escapes['\''] = ''
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


def get_five_longest_entries(summary, top=5):
    sorted_summary = dict()
    if len(summary) < 6:
        return summary
    for key in sorted(summary, key=lambda key: len(summary[key]), reverse=True):
        sorted_summary.update({key: summary[key]})
        if len(sorted_summary) == top:
            return sorted_summary
    return sorted_summary


def exploit_mitigation(summary):
    summary = summary['exploit_mitigations']['summary']
    max_count = count_mitigations(summary)  # bar is maxed at 6
    pie_num, canary_num, relro_num, nx_num, fortify_num = 0, 0, 0, 0, 0
    for selected_summary in summary:
        if 'PIE' in selected_summary and 'present' in selected_summary:
            pie_num += len(summary[selected_summary])
        if 'RELRO' in selected_summary and 'enabled' in selected_summary:
            relro_num += len(summary[selected_summary])
        if 'Canary' in selected_summary and 'enabled' in selected_summary:
            canary_num += len(summary[selected_summary])
        if 'NX' in selected_summary and 'enabled' in selected_summary:
            nx_num += len(summary[selected_summary])
        if 'FORTIFY' in selected_summary and 'enabled' in selected_summary:
            fortify_num += len(summary[selected_summary])
    return '{0}{2}/{3}{1},{0}{4}/{5}{1},' \
           '{0}{6}/{7}{1},{0}{8}/{9}{1},' \
           '{0}{10}/{11}{1}'.format('{', '}', 'CANARY', canary_num * 6 / max_count, 'PIE', pie_num * 6 / max_count,
                                    'RELRO', relro_num * 6 / max_count, 'NX', nx_num * 6 / max_count,
                                    'FORTIFY\_SOURCE', fortify_num * 6 / max_count)


def count_mitigations(summary):
    for mitigation in ['Canary', 'NX', 'RELRO', 'PIE', 'FORTIFY']:
        count = count_this_mitigation(summary, mitigation)
        if count != 0:
            return count
    return count


def count_this_mitigation(summary, mitigation):
    count = 0
    for selected_summary in summary:
        if mitigation in selected_summary:
            count += len(summary[selected_summary])
    return count


def software_components(software_string):
    software = software_string
    ver_number = ''
    if ' ' in software_string:
        if len(software_string.split(' ')) > 2:
            software = ''.join(software_string.split(' ')[:-1])
            ver_number = software_string.split(' ')[-1]
            try:
                int(ver_number[0])
            except ValueError:
                ver_number, software = software, ver_number
        elif isinstance(software_string.split(' '), list) and len(software_string.split(' ')[1]) > 0:
            software, ver_number = software_string.split(' ')
            try:
                int(ver_number[0])
            except ValueError:
                ver_number, software = software, ver_number
    return '{}{}{}{}'.format(ver_number, '}', '{', software)


def get_triples(analysis):
    combined_triples = []
    for desired in ['IPv4', 'IPv6', 'URI ']:
        combined_triples.append(get_desired_triple(analysis, desired))
    return combined_triples


def get_desired_triple(seleced_summary, which_desired):
    desired_list = ip_or_uri(seleced_summary, which_desired)
    chosen_one = 'x x' * 60
    while len(chosen_one) > 50:
        chosen_one = choice(desired_list)
    return '{2}{1}{0}{3}{4}$\>$ (incl. {5})'.format('{', '}', len(desired_list), which_desired, '\quad',
                                                    replace_special_characters(chosen_one))


def ip_or_uri(summary, which_select):
    new_list = []
    for data in summary:
        if ('URI ' in which_select and not _validate_ip(data, socket.AF_INET) and not _validate_ip(data,
                                                                                                   socket.AF_INET6)):
            new_list.append(data)
        elif 'IPv4' in which_select and _validate_ip(data, socket.AF_INET):
            new_list.append(data)
        elif 'IPv6' in which_select and _validate_ip(data, socket.AF_INET6):
            new_list.append(data)
    return new_list


def _validate_ip(ip, address_format):
    try:
        _ = socket.inet_pton(address_format, ip)
        return True
    except OSError:
        return False


def get_x_entries(summary, how_many=10):
    if len(summary) <= how_many:
        return summary
    else:
        return summary[:how_many]


def _add_filters_to_jinja(environment):
    environment.filters['number_format'] = render_number_as_size
    environment.filters['nice_unix_time'] = render_unix_time
    environment.filters['filter_chars'] = replace_special_characters
    environment.filters['elements_count'] = len
    environment.filters['base64_to_png'] = decode_base64_to_file
    environment.filters['top_five'] = get_five_longest_entries
    environment.filters['sort'] = sorted
    environment.filters['call_for_mitigations'] = exploit_mitigation
    environment.filters['split_space'] = software_components
    environment.filters['triplet'] = get_triples
    environment.filters['x_entires'] = get_x_entries


class TemplateEngine:
    def __init__(self, template_folder=None, tmp_dir=None):
        self._environment = create_jinja_environment(template_folder if template_folder else 'default')
        self._tmp_dir = tmp_dir

    def render_main_template(self, analysis):
        template = self._environment.get_template(MAIN_TEMPLATE)
        return template.render(analysis=analysis, tmp_dir=self._tmp_dir)

    def render_meta_template(self, meta_data):
        template = self._environment.get_template(META_TEMPLATE)
        return template.render(meta_data=meta_data)

    def render_template_class(self):
        template = self._environment.get_template(CUSTOM_TEMPLATE_CLASS)
        return template.render(tmp_dir=self._tmp_dir)
