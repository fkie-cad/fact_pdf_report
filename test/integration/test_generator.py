import pytest
from pdf_generator.tex_generation.template_engine import TemplateEngine
from test.data.test_dict import TEST_DICT

# pylint: disable=redefined-outer-name

TEST_DATA = {
    'analysis': {'file_hashes': {'ssdeep': 'bla', 'sha1': 'blah'}},
    'meta_data': {'device_name': 'test_device'}
}


@pytest.fixture(scope='function')
def stub_engine():
    return TemplateEngine()


def test_latex_code_generation(stub_engine: TemplateEngine):
    result = stub_engine.render_meta_template(TEST_DICT)
    assert result


def test_render_template(tmpdir):
    engine = TemplateEngine(template_folder='test', tmp_dir=tmpdir)
    test_data = {'meta_data': '123', 'analysis': '456'}
    output = engine.render_analysis_template(plugin='render_test', analysis=test_data)

    assert output == 'Test  - '
