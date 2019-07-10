from pathlib import Path

from pdf_generator.tex_generation.template_engine import (
    byte_number_filter, convert_base64_to_png_filter, nice_number_filter, nice_unix_time, split_hash, split_output_lines
)


def test_byte_number_filter():
    assert byte_number_filter(None) == 'not available'

    assert byte_number_filter(12, verbose=False) == '12.00 Byte'
    assert byte_number_filter(128000) == '125.00 KiB (128,000 Byte)'
    assert byte_number_filter(128000, verbose=False) == '125.00 KiB'


def test_nice_number_filter():
    assert nice_number_filter(None) == 'not available'
    assert nice_number_filter('no int') == 'not available'

    assert nice_number_filter(12) == '12'
    assert nice_number_filter(12.1) == '12.10'
    assert nice_number_filter(12.101) == '12.10'
    assert nice_number_filter(12.109) == '12.11'
    assert nice_number_filter('12') == '12'


def test_nice_unix_time():
    assert nice_unix_time(None) == 'not available'

    assert nice_unix_time(10) == '1970-01-01 01:00:10'


def test_split_hash():
    assert split_hash('X' * 62) == '{} X'.format('X' * 61)
    assert split_hash('X' * 61) == 'X' * 61


def test_split_output_lines():
    assert split_output_lines('X\nX') == 'X\nX'
    assert split_output_lines('{}\nX'.format('X' * 93)) == '{} X\nX'.format('X' * 92)


def test_convert_base64_to_png_filter(tmpdir):
    convert_base64_to_png_filter('0000', 'testfile', str(tmpdir))
    assert Path(str(tmpdir), 'testfile.png').read_bytes() == b'\xd3\x4d\x34'
