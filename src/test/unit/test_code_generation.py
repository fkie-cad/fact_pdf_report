from tempfile import TemporaryDirectory
from pathlib import Path
from latex_code_generation.code_generation import _set_jinja_env, _render_analysis_result, _create_tex_files, generate_pdf_report


def test_render_template():
    test_data = {'meta_data': '123', 'analysis': '456'}
    jinja_env = _set_jinja_env(templates_to_use='test')
    output = _render_analysis_result(test_data, jinja_env, 'render_test')
    assert output == 'Test 123 - 456'


def test_create_tex_files():
    test_data = {'analysis': {'file_hashes': {'ssdeep': 'bla', 'sha1': 'blah'}, 'meta_data': dict()}}
    tmp_dir = TemporaryDirectory()
    jinja_env = _set_jinja_env(templates_to_use='default')
    for template_name in test_data['analysis']:
        _create_tex_files(test_data, jinja_env)
        file_path = Path(tmp_dir.name, template_name + '.tex')
        assert file_path.exists()


def test_main():
    generate_pdf_report(firmware_uid='b79ea608e2f0390744642bad472f8d9fd7e4713791857da5d5fcabf70a009e50_29626948')

