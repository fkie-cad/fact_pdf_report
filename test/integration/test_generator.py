import pytest
from pdf_generator.generator import generate_report
from pdf_generator.tex_generation.template_engine import Engine
from test.data.test_dict import TEST_DICT

# pylint: disable=redefined-outer-name

TEST_DATA = {
    'analysis': {'file_hashes': {'ssdeep': 'bla', 'sha1': 'blah'}},
    'meta_data': {'device_name': 'test_device'}
}


@pytest.fixture(scope='function')
def stub_engine():
    return Engine()


def test_latex_code_generation(stub_engine: Engine):
    result = stub_engine.render_meta_template(TEST_DICT)
    assert result


def test_render_template(tmpdir):
    engine = Engine(template_folder='test', tmp_dir=tmpdir)
    test_data = {'meta_data': '123', 'analysis': '456'}
    output = engine.render_analysis_template(plugin='render_test', analysis=test_data)

    assert output == 'Test  - '


def test_main(monkeypatch):
    monkeypatch.setattr('pdf_generator.generator.request_firmware_data', lambda *_: (TEST_DATA['analysis'], TEST_DATA['meta_data']))
    monkeypatch.setattr('pdf_generator.generator.shutil.move', lambda *_: None)
    generate_report(firmware_uid='b79ea608e2f0390744642bad472f8d9fd7e4713791857da5d5fcabf70a009e50_29626948')
