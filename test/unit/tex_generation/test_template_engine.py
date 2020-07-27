from pathlib import Path

import pytest
from pdf_generator.tex_generation.template_engine import (
    software_components, TemplateEngine, decode_base64_to_file, render_number_as_size, render_unix_time,
    replace_special_characters, get_five_longest_entries
)

from test.data.test_dict import TEST_DICT

# pylint: disable=redefined-outer-name


@pytest.fixture(scope='function')
def stub_engine(tmpdir):
    return TemplateEngine(template_folder='test', tmp_dir=tmpdir)


def test_byte_number_filter():
    assert render_number_as_size(None) == 'not available'

    assert render_number_as_size(12, verbose=False) == '12.00 Byte'
    assert render_number_as_size(128000) == '125.00 KiB (128,000 Byte)'
    assert render_number_as_size(128000, verbose=False) == '125.00 KiB'


@pytest.mark.skip(reason='Since local time used, result is not stable')
def test_nice_unix_time():
    assert render_unix_time(None) == 'not available'

    assert render_unix_time(10) == '1970-01-01 01:00:10'


def test_convert_base64_to_png_filter(tmpdir):
    decode_base64_to_file('0000', 'testfile', str(tmpdir))
    assert Path(str(tmpdir), 'testfile.png').read_bytes() == b'\xd3\x4d\x34'


def test_filter_latex_special_chars():
    assert replace_special_characters('safe') == 'safe'

    assert replace_special_characters(r'C:\Windows') == r'C:Windows'
    assert replace_special_characters(r'100 $') == r'100 \$'


def test_render_meta_template(stub_engine):
    assert stub_engine.render_meta_template(meta_data='anything') == 'Test anything - '


def test_render_main_template(stub_engine):
    assert stub_engine.render_main_template(analysis='else') == 'Test  - else'


def test_get_five_longest_entries():
    assert len(get_five_longest_entries(TEST_DICT['file_type']['summary'], top=3)) <= 3
    longest_dict = get_five_longest_entries(TEST_DICT['file_type']['summary'], top=1)
    assert len(longest_dict) == 1
    assert 'compression/zlib' in longest_dict.keys()


@pytest.mark.parametrize('test_input, expected_output', [
    ('FOO 1.0', '1.0}{FOO'),
    ('1.0 FOO', '1.0}{FOO'),
    ('FOO BAR 1.0', '1.0}{FOOBAR'),
    ('FOO', '}{FOO'),
    ('  FOO  ', '}{FOO'),
    ('  FOO  BAR  1.0  ', '1.0}{FOOBAR'),
])
def test_software_components(test_input, expected_output):
    assert software_components(test_input) == expected_output
