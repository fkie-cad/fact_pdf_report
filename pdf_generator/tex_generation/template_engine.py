from base64 import decodebytes
from collections import OrderedDict
from pathlib import Path
from time import localtime, strftime

from random import choice
import socket
from typing import List

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
    if len(summary) < top + 1:
        return summary
    for key in sorted(summary, key=lambda key: len(summary[key]), reverse=True):
        sorted_summary.update({key: summary[key]})
        if len(sorted_summary) == top:
            return sorted_summary
    return sorted_summary


def exploit_mitigation(summary):
    summary = summary['exploit_mitigations']['summary']
    max_count = _count_mitigations(summary)
    numbers = dict()
    for key in ['PIE', 'RELRO', 'Canary', 'NX', 'FORTIFY']:
        numbers[key] = _count_occurrences(key, summary)
    return (
        f'{{CANARY/{numbers["Canary"] / max_count}}},{{PIE/{numbers["PIE"] / max_count}}},'
        f'{{RELRO/{numbers["RELRO"] / max_count}}},{{NX/{numbers["NX"] / max_count}}},'
        f'{{FORTIFY\\_SOURCE/{numbers["FORTIFY"] / max_count}}}'
    )


def _count_occurrences(key, summary):
    return sum(
        len(summary[entry])
        for entry in summary
        if key in entry and ('present' in entry or 'enabled' in entry)
    )


def _count_mitigations(summary):
    for mitigation in ['Canary', 'NX', 'RELRO', 'PIE', 'FORTIFY']:
        count = _count_this_mitigation(summary, mitigation)
        if count != 0:
            return count
    if count == 0:
        count = 1
    return count


def _count_this_mitigation(summary, mitigation):
    count = 0
    for selected_summary in summary:
        if mitigation in selected_summary:
            count += len(summary[selected_summary])
    return count


def software_components(software_string):
    software = software_string.strip()
    ver_number = ''
    if ' ' in software:
        split_software_string = software.split(' ')
        if len(split_software_string) > 2:
            software, ver_number = _larger_two_components(split_software_string)
        elif len(split_software_string[1]) > 0:
            software, ver_number = _less_three_components(split_software_string)
    return f'{ver_number}}}{{{replace_special_characters(software)}'


def _less_three_components(software_string):
    software, ver_number = software_string
    return _order_components(software, ver_number)


def _larger_two_components(software_string):
    software = ''.join(software_string[:-1])
    ver_number = software_string[-1]
    return _order_components(software, ver_number)


def _order_components(software, ver_number):
    try:
        int(ver_number[0])
    except ValueError:
        return ver_number, software
    return software, ver_number


def aggregate_ip_stats(summary_of_ip_analysis: dict) -> List[str]:
    uris, ipv4s, ipv6s = _sort_ip_analysis_results(summary_of_ip_analysis)
    return [
        _aggregate_ip_class(ipv4s, 'IPv4'),
        _aggregate_ip_class(ipv6s, 'IPv6'),
        _aggregate_ip_class(uris, 'URI'),
    ]


def _aggregate_ip_class(elements_of_ip_class, ip_class):
    if not elements_of_ip_class:
        return f'0}}{{{ip_class}\\quad$\\>$'

    return (
        f'{len(elements_of_ip_class)}}}{{{ip_class}\\quad$\\>$ '
        f'(incl. {replace_special_characters(_find_short_element(elements_of_ip_class, 50))})'
    )


def _find_short_element(elements_of_ip_class, max_length):
    for element in elements_of_ip_class:
        if len(element) <= max_length:
            return element
    return elements_of_ip_class[0][:51]


def _sort_ip_analysis_results(summary_of_ip_analysis):
    uris, ipv4s, ipv6s = [], [], []
    for element in summary_of_ip_analysis:
        if not _validate_ip(element, socket.AF_INET) and not _validate_ip(element, socket.AF_INET6):
            uris.append(element)
        elif _validate_ip(element, socket.AF_INET):
            ipv4s.append(element)
        else:
            ipv6s.append(element)
    return uris, ipv4s, ipv6s


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


def cve_criticals(summary):
    f_string = []
    else_count = len(summary)
    for cve in summary:
        if 'CRITICAL' in cve:
            f_string.append(cve)
            else_count -= 1
    f_string.append(f'and {else_count} other uncritical')
    return f_string


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
    environment.filters['aggregate_ip_stats'] = aggregate_ip_stats
    environment.filters['x_entries'] = get_x_entries
    environment.filters['cve_crits'] = cve_criticals


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
