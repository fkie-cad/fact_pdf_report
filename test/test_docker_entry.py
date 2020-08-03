from pathlib import Path
import shutil

import PyPDF2

from docker_entry import main as main_docker_entry

# pylint: disable=redefined-outer-name
INTERFACE_DIR = Path('/tmp/interface')
OUTPUT_FILE = INTERFACE_DIR / 'pdf' / 'A_devices_name_analysis_report.pdf'
TEST_META_DATA = Path(__file__).parent / 'data' / 'meta.json'
TEST_ANALYSIS_DATA = Path(__file__).parent / 'data' / 'analysis.json'


def test_docker_entry():
    (INTERFACE_DIR / 'data').mkdir(parents=True, exist_ok=True)
    (INTERFACE_DIR / 'pdf').mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TEST_ANALYSIS_DATA, INTERFACE_DIR / 'data' / 'analysis.json')
    shutil.copyfile(TEST_META_DATA, INTERFACE_DIR / 'data' / 'meta.json')
    output = main_docker_entry()
    assert output == 0, 'LaTeX PDF build unsuccessful'

    assert OUTPUT_FILE.is_file()
    try:
        PyPDF2.PdfFileReader(open(str(OUTPUT_FILE), 'rb'))
    except PyPDF2.utils.PdfReadError:
        assert False, 'PDF could not be read'
