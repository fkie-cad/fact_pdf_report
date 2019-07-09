from pathlib import Path

import pytest
from common_helper_process.fail_safe_subprocess import execute_shell_command_get_return_code

SCRIPT_PATH = Path(__file__).parent.parent.parent / 'pdf_generator' / 'pdf_generator.py'


@pytest.mark.parametrize('arguments, expected_output, expected_return_code', [
    ('-V', 'FACT', 0),
    ('-h', 'usag', 0)
])
def test_main_program(arguments, expected_output, expected_return_code):
    command_line = str(SCRIPT_PATH) + ' ' + arguments
    output, return_code = execute_shell_command_get_return_code(command_line)
    assert output[0:4] == expected_output
    assert return_code == expected_return_code
