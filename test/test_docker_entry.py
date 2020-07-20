import PyPDF2

from docker_entry import main as main_docker_entry
import pathlib
import shutil


# pylint: disable=redefined-outer-name

def test_docker_entry(template_style='default'):
    pathlib.Path("/tmp/interface/data").mkdir(parents=True, exist_ok=True)
    pathlib.Path("/tmp/interface/pdf").mkdir(parents=True, exist_ok=True)
    shutil.copyfile('data/analysis.json', '/tmp/interface/data/analysis.json')
    shutil.copyfile('data/meta.json', '/tmp/interface/data/meta.json')
    output = main_docker_entry()

    try:
        PyPDF2.PdfFileReader(open('/tmp/interface/pdf/A_devices_name_analysis_report.pdf', "rb"))
    except PyPDF2.utils.PdfReadError:
        assert False
    assert pathlib.Path('/tmp/interface/pdf/A_devices_name_analysis_report.pdf').exists()
    assert output == 0
