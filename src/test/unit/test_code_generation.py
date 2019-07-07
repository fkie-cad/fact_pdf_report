from tempfile import TemporaryDirectory

from latex_code_generation.code_generation import _render_analysis_result, create_jinja_environment, generate_pdf_report

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
    monkeypatch.setattr('latex_code_generation.code_generation.request_firmware_data', lambda *_: (TEST_DATA['analysis'], TEST_DATA['meta_data']))
    monkeypatch.setattr('latex_code_generation.code_generation.shutil.move', lambda *_: None)
    generate_pdf_report(firmware_uid='b79ea608e2f0390744642bad472f8d9fd7e4713791857da5d5fcabf70a009e50_29626948')
