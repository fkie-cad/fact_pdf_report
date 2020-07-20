import pytest
from pdf_generator.tex_generation.template_engine import TemplateEngine
from test.data.test_dict import TEST_DICT, META_DICT


# pylint: disable=redefined-outer-name


@pytest.fixture(scope='function')
def stub_engine():
    return TemplateEngine()


def test_latex_code_generation(stub_engine: TemplateEngine):
    result = stub_engine.render_meta_template(META_DICT)
    assert result


def test_render_template(stub_engine, tmpdir):
    output = stub_engine.render_main_template(analysis=[TEST_DICT, META_DICT])
    assert output
