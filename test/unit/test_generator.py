import json
from pathlib import Path

import pytest
from pdf_generator.generator import (
    copy_fact_image, create_report_filename, create_templates, execute_latex, render_analysis_templates
)


class MockEngine:
    def __init__(self, *_, **__):
        pass

    @staticmethod
    def render_main_template(analysis, meta_data):
        return '{}\n{}'.format(json.dumps(analysis), json.dumps(meta_data))

    @staticmethod
    def render_meta_template(meta_data):
        return json.dumps(meta_data)

    @staticmethod
    def render_analysis_template(_, analysis):
        return json.dumps(analysis)


def exec_mock(*_, **__):
    Path('test').write_text('works')


def test_execute_latex(monkeypatch, tmpdir):
    monkeypatch.setattr('pdf_generator.generator.execute_shell_command', exec_mock)

    execute_latex(str(tmpdir))
    assert Path(str(tmpdir), 'test').exists()
    assert Path(str(tmpdir), 'test').read_text() == 'works'


def test_copy_fact_image(tmpdir):
    copy_fact_image(str(tmpdir))
    assert Path(str(tmpdir), 'fact_logo.png').exists()


@pytest.mark.parametrize('device_name, pdf_name', [
    ('simple', 'simple_analysis_report.pdf'),
    ('harder name', 'harder_name_analysis_report.pdf'),
    ('dangerous/name', 'dangerous__name_analysis_report.pdf')
])
def test_create_report_filename(device_name, pdf_name):
    assert create_report_filename({'device_name': device_name}) == pdf_name


def test_create_analysis_templates():
    templates = render_analysis_templates(engine=MockEngine(), analysis={'test': {'result': 'data'}})

    assert len(templates) == 1

    filename, result_code = templates[0]
    assert filename == 'test.tex'
    assert result_code == '{"result": "data"}'


def test_create_templates(monkeypatch, tmpdir):
    monkeypatch.setattr('pdf_generator.generator.TemplateEngine', MockEngine)
    create_templates(analysis={'test': {'result': 'data'}}, meta_data={}, tmp_dir=str(tmpdir))

    assert Path(str(tmpdir), 'main.tex').exists()
    assert Path(str(tmpdir), 'meta.tex').exists()
    assert Path(str(tmpdir), 'test.tex').exists()

    assert Path(str(tmpdir), 'test.tex').read_text() == '{"result": "data"}'
