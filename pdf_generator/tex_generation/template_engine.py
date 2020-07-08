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

LATEX_CHARACTER_ESCAPES = OrderedDict([
    ('\\', ''),
    ('\'', ''),
    ('$', '\\$'),
    ('(', '$($'),
    (')', '$)$'),
    ('[', '$[$'),
    (']', '$]$'),
    ('#', '\\#'),
    ('%', '\\%'),
    ('&', '\\&'),
    ('_', '\\_'),
    ('{', '\\{'),
    ('}', '\\}'),
    ('^', '\\textasciicircum{}'),
    ('~', '\\textasciitilde{}'),
    ('>', '\\textgreater{}'),
    ('<', '\\textless{}'),
    ('\n', '\\newline ')
])


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
    for character, replacement in LATEX_CHARACTER_ESCAPES.items():
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
    if len(summary) < top+1:
        return summary
    for key in sorted(summary, key=lambda key: len(summary[key]), reverse=True):
        sorted_summary.update({key: summary[key]})
        if len(sorted_summary) == top:
            return sorted_summary
    return sorted_summary


def exploit_mitigation(summary):
    summary = summary['exploit_mitigations']['summary']
    max_count = count_mitigations(summary)
    numbers = dict()
    for key in ['PIE', 'RELRO', 'Canary', 'NX', 'FORTIFY']:
        numbers[key] = count_occurrences(key, summary)
    return (
        f'{{CANARY/{numbers["Canary"] / max_count}}},{{PIE/{numbers["PIE"] / max_count}}},'
        f'{{RELRO/{numbers["RELRO"] / max_count}}},{{NX/{numbers["NX"] / max_count}}},'
        f'{{FORTIFY\\_SOURCE/{numbers["FORTIFY"] / max_count}}}'
    )


def count_occurrences(key, summary):
    return sum(
        len(summary[entry])
        for entry in summary
        if key in entry and ('present' in entry or 'enabled' in entry)
    )


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
        splitted_software_string = software_string.split(' ')
        if len(splitted_software_string) > 2:
            software, ver_number = larger_two_components(splitted_software_string)
        elif len(splitted_software_string[1]) > 0:
            software, ver_number = less_three_components(splitted_software_string)
    return f'{ver_number}}}{{{software}'


def less_three_components(software_string):
    software, ver_number = software_string
    try:
        int(ver_number[0])
    except ValueError:
        return ver_number, software
    return software, ver_number


def larger_two_components(software_string):
    software = ''.join(software_string[:-1])
    ver_number = software_string[-1]
    try:
        int(ver_number[0])
    except ValueError:
        return ver_number, software
    return software, ver_number


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
    return f'{len(desired_list)}}}{{{which_desired}\\quad$\\>$ (incl. {replace_special_characters(chosen_one)})'


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
