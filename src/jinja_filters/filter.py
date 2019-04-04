from base64 import decodebytes
from time import localtime, strftime

from common_helper_files import human_readable_file_size


def byte_number_filter(number, verbose=True):
    if isinstance(number, int) or isinstance(number, float):
        if verbose:
            return '{} ({})'.format(human_readable_file_size(int(number)), format(number, ',d') + ' bytes')
        return human_readable_file_size(int(number))
    return 'not available'


def nice_unix_time(unix_time_stamp):
    '''
    input unix_time_stamp
    output string 'YYYY-MM-DD HH:MM:SS'
    '''
    if isinstance(unix_time_stamp, float) or isinstance(unix_time_stamp, int):
        tmp = localtime(unix_time_stamp)
        return strftime('%Y-%m-%d %H:%M:%S', tmp)
    else:
        return unix_time_stamp


def nice_number_filter(i):
    if isinstance(i, int):
        return '{:,}'.format(i)
    elif isinstance(i, float):
        return '{:,.2f}'.format(i)
    elif i is None:
        return 'not available'
    else:
        return i


def filter_latex_special_chars(data):
    if "\\" in data:
        data = data.replace("\\", "")
    if "$" in data:
        data = data.replace("$", "\\$")
    if "(" in data:
        data = data.replace("(", "$($")
    if ")" in data:
        data = data.replace(")", "$)$")
    if "[" in data:
        data = data.replace("[", "$[$")
    if "]" in data:
        data = data.replace("]", "$]$")
    if "#" in data:
        data = data.replace("#", "\\#")
    if "%" in data:
        data = data.replace("%", "\\%")
    if "&" in data:
        data = data.replace("&", "\\&")
    if "_" in data:
        data = data.replace("_", "\\_")
    if "{" in data:
        data = data.replace("{", "\\{")
    if "}" in data:
        data = data.replace("}", "\\}")
    if "^" in data:
        data = data.replace("^", "\\textasciicircum{}")
    if "~" in data:
        data = data.replace("~", "\\textasciitilde{}")
    if ">" in data:
        data = data.replace(">", "\\textgreater{}")
    if "<" in data:
        data = data.replace("<", "\\textless{}")
    if "\n" in data:
        data = data.replace("\n", "\\newline ")
    if "\'" in data:
        data = data.replace("\'", "")
    return data


def count_elements_in_list(ls):
    return len(ls)


def convert_base64_to_png_filter(s, filename):
    base64_encoded = s.encode('utf-8')
    png_filename = filename + ".png"
    with open(png_filename, "wb") as fh:
        fh.write(decodebytes(base64_encoded))

    return png_filename


def check_if_list_empty(ls):
    if ls:
        return ls
    else:
        empty_ls = ['list is empty']
        return empty_ls


def split_hash(hash_value):
    if len(hash_value) > 61:
        hash_value = hash_value[:61] + ' ' + hash_value[61:]
    return hash_value


def split_output_lines(output_value):
    splited_lines = output_value.splitlines()
    output = ''

    for line in splited_lines:
        line_length = len(line)
        # word_lengths.append(list(map(len, line.split(" "))))
        if line_length > 92:
            line = line[:92] + ' ' + line[92:]
        output += line + "\n"
    return output