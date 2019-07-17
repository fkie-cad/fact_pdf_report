from pathlib import Path

import pytest
from pdf_generator.tex_generation.template_engine import (
    TemplateEngine, decode_base64_to_file, render_number_as_size, render_number_as_string, render_unix_time,
    replace_characters_in_list, replace_special_characters, split_hash_string, split_long_lines
)

# pylint: disable=redefined-outer-name


@pytest.fixture(scope='function')
def stub_engine(tmpdir):
    return TemplateEngine(template_folder='test', tmp_dir=tmpdir)


def test_byte_number_filter():
    assert render_number_as_size(None) == 'not available'

    assert render_number_as_size(12, verbose=False) == '12.00 Byte'
    assert render_number_as_size(128000) == '125.00 KiB (128,000 Byte)'
    assert render_number_as_size(128000, verbose=False) == '125.00 KiB'


def test_nice_number_filter():
    assert render_number_as_string(None) == 'not available'
    assert render_number_as_string('no int') == 'not available'

    assert render_number_as_string(12) == '12'
    assert render_number_as_string(12.1) == '12.10'
    assert render_number_as_string(12.101) == '12.10'
    assert render_number_as_string(12.109) == '12.11'
    assert render_number_as_string('12') == '12'


@pytest.mark.skip(reason='Since local time used, result is not stable')
def test_nice_unix_time():
    assert render_unix_time(None) == 'not available'

    assert render_unix_time(10) == '1970-01-01 01:00:10'


def test_split_hash():
    assert split_hash_string('X' * 62) == '{}\nX'.format('X' * 61)
    assert split_hash_string('X' * 61) == 'X' * 61


def test_split_output_lines():
    assert split_long_lines('X\nX') == 'X\nX'
    assert split_long_lines('{}\nX'.format('X' * 93)) == '{}\nX\nX'.format('X' * 92)


def test_convert_base64_to_png_filter(tmpdir):
    decode_base64_to_file('0000', 'testfile', str(tmpdir))
    assert Path(str(tmpdir), 'testfile.png').read_bytes() == b'\xd3\x4d\x34'


def test_filter_latex_special_chars():
    assert replace_special_characters('safe') == 'safe'

    assert replace_special_characters(r'C:\Windows') == r'C:Windows'
    assert replace_special_characters(r'100 $') == r'100 \$'


def test_filter_chars_in_list():
    assert replace_characters_in_list([]) == []

    assert replace_characters_in_list([r'safe', r'un\safe']) == ['safe', 'unsafe']


def test_render_meta_template(stub_engine):
    assert stub_engine.render_meta_template(meta_data='anything') == 'Test anything - '


def test_render_main_template(stub_engine):
    assert stub_engine.render_main_template(meta_data='anything', analysis='else') == 'Test anything - else'


def test_render_analysis_template(stub_engine):
    assert stub_engine.render_analysis_template(plugin='non_existing', analysis='result') == 'Presenting: result'
