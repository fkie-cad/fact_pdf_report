from tempfile import TemporaryDirectory
from pathlib import Path
from latex_code_generation.code_generation import _set_jinja_env, _render_template, _write_file, _create_tex_files


def test_render_template():
    test_data = {'meta_data': '123', 'analysis': '456'}
    jinja_env = _set_jinja_env(templates_to_use='test')
    output = _render_template(test_data, jinja_env, 'render_test')
    assert output == 'Test 123 - 456'


def test_write_file():
    tmp_dir = TemporaryDirectory()
    file_path = Path(tmp_dir.name, 'test.tex')
    _write_file('test', file_path)
    assert file_path.exists()


def test_create_tex_files():
    test_data = {'analysis': {'file_hashes': {'ssdeep': 'bla', 'sha1': 'blah'}, 'meta_data': dict()}}
    tmp_dir = TemporaryDirectory()
    jinja_env = _set_jinja_env(templates_to_use='default')
    for template_name in test_data['analysis']:
        _create_tex_files(test_data, jinja_env)
        file_path = Path(tmp_dir.name, template_name + '.tex')
        assert file_path.exists()
