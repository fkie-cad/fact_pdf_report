import json
from pathlib import Path

import pytest
from pdf_generator.generator import (
    LOGO_FILE, MAIN_TEMPLATE, META_TEMPLATE, copy_fact_image, create_report_filename,
    create_templates, execute_latex
)
from test.data.test_dict import TEST_DICT, META_DICT


class MockEngine:
    def __init__(self, *_, **__):
        pass

    @staticmethod
    def render_main_template(analysis):
        return '{}'.format(json.dumps(analysis))

    @staticmethod
    def render_meta_template(meta_data):
        return json.dumps(meta_data)

    @staticmethod
    def render_analysis_template(_, analysis):
        return json.dumps(analysis)

    @staticmethod
    def render_template_class():
        return json.dumps('template_class.cls')


def exec_mock(*_, **__):
    Path('test').write_text('works')


def test_execute_latex(monkeypatch, tmpdir):
    monkeypatch.setattr('pdf_generator.generator.execute_shell_command', exec_mock)

    execute_latex(str(tmpdir))
    assert Path(str(tmpdir), 'test').exists()
    assert Path(str(tmpdir), 'test').read_text() == 'works'


def test_copy_fact_image(tmpdir):
    copy_fact_image(str(tmpdir))
    assert Path(str(tmpdir), LOGO_FILE).exists()


@pytest.mark.parametrize('device_name, pdf_name', [
    ('simple', 'simple_analysis_report.pdf'),
    ('harder name', 'harder_name_analysis_report.pdf'),
    ('dangerous/name', 'dangerous__name_analysis_report.pdf')
])
def test_create_report_filename(device_name, pdf_name):
    assert create_report_filename({'device_name': device_name}) == pdf_name


def test_create_templates(monkeypatch, tmpdir):
    monkeypatch.setattr('pdf_generator.generator.TemplateEngine', MockEngine)
    create_templates(analysis=TEST_DICT, meta_data=META_DICT, tmp_dir=str(tmpdir))

    assert Path(str(tmpdir), MAIN_TEMPLATE).exists()
    assert Path(str(tmpdir), META_TEMPLATE).exists()
