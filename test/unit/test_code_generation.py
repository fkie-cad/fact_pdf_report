from tempfile import TemporaryDirectory

from pdf_generator.generator import generate_report
from pdf_generator.tex_generation.template_engine import Engine

TEST_DATA = {
    'analysis': {'file_hashes': {'ssdeep': 'bla', 'sha1': 'blah'}},
    'meta_data': {'device_name': 'test_device'}
}


def test_render_template():
    with TemporaryDirectory() as tmp_dir:
        engine = Engine(template_folder='test', tmp_dir=tmp_dir)
        test_data = {'meta_data': '123', 'analysis': '456'}
        output = engine.render_analysis_template(plugin='render_test', analysis=test_data)

    assert output == 'Test  - '


def test_main(monkeypatch):
    monkeypatch.setattr('pdf_generator.generator.request_firmware_data', lambda *_: (TEST_DATA['analysis'], TEST_DATA['meta_data']))
    monkeypatch.setattr('pdf_generator.generator.shutil.move', lambda *_: None)
    generate_report(firmware_uid='b79ea608e2f0390744642bad472f8d9fd7e4713791857da5d5fcabf70a009e50_29626948')
