import json
from pathlib import Path

from pdf_generator.generator import (
    copy_fact_image, create_report_filename, create_templates, execute_latex, generate_analysis_templates
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
    monkeypatch.setattr('pdf_generator.generator.execute_shell_command_get_return_code', exec_mock)

    execute_latex(tmpdir)
    assert Path(tmpdir, 'test').exists()
    assert Path(tmpdir, 'test').read_text() == 'works'


def test_copy_fact_image(tmpdir):
    copy_fact_image(tmpdir)
    assert Path(tmpdir, 'fact_logo.png').exists()


def test_create_report_filename():
    assert create_report_filename({'device_name': 'simple'}) == 'simple_analysis_report.pdf'
    assert create_report_filename({'device_name': 'harder name'}) == 'harder_name_analysis_report.pdf'
    assert create_report_filename({'device_name': 'dangerous/name'}) == 'dangerous__name_analysis_report.pdf'


def test_create_analysis_templates():
    templates = generate_analysis_templates(engine=MockEngine(), analysis={'test': {'result': 'data'}})

    assert len(templates) == 1

    filename, result_code = templates[0]
    assert filename == 'test.tex'
    assert result_code == '{"result": "data"}'


def test_create_templates(monkeypatch, tmpdir):
    monkeypatch.setattr('pdf_generator.generator.Engine', MockEngine)
    create_templates(analysis={'test': {'result': 'data'}}, meta_data={}, tmp_dir=tmpdir)

    assert Path(tmpdir, 'main.tex').exists()
    assert Path(tmpdir, 'meta.tex').exists()
    assert Path(tmpdir, 'test.tex').exists()

    assert Path(tmpdir, 'test.tex').read_text() == '{"result": "data"}'