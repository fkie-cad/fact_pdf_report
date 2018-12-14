from common_helper_process.fail_safe_subprocess import execute_shell_command_get_return_code
import os


SRC_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../../pdf_generator.py'


def test_main_program():
    command_line = SRC_DIR + ' -V'
    output, return_code = execute_shell_command_get_return_code(command_line)
    print(output)
    assert return_code == 0
