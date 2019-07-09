from tempfile import TemporaryDirectory

from pdf_generator.pdf_generator import main
from pdf_generator.tex_generation.code_generation import _render_analysis_result
from pdf_generator.tex_generation.template_engine import create_jinja_environment

TEST_DATA = {
    'analysis': {'file_hashes': {'ssdeep': 'bla', 'sha1': 'blah'}},
    'meta_data': {'device_name': 'test_device'}
}


def test_render_template():
    with TemporaryDirectory() as tmp_dir:
        test_data = {'meta_data': '123', 'analysis': '456'}
        jinja_env = create_jinja_environment(templates_to_use='test')
        output = _render_analysis_result(test_data, jinja_env, 'render_test', tmp_dir)

    assert output == 'Test  - '


def test_main(monkeypatch):
    monkeypatch.setattr('pdf_generator.pdf_generator.request_firmware_data', lambda *_: (TEST_DATA['analysis'], TEST_DATA['meta_data']))
    monkeypatch.setattr('pdf_generator.pdf_generator.shutil.move', lambda *_: None)
    main(firmware_uid='b79ea608e2f0390744642bad472f8d9fd7e4713791857da5d5fcabf70a009e50_29626948')
