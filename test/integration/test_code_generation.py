import pytest
from pdf_generator.tex_generation.template_engine import Engine
from test.data.test_dict import TEST_DICT

# pylint: disable=redefined-outer-name


@pytest.fixture(scope='function')
def stub_engine():
    return Engine()


def test_latex_code_generation(stub_engine: Engine):
    result = stub_engine.render_meta_template(TEST_DICT)
    assert result
