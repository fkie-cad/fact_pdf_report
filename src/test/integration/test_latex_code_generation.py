from tempfile import TemporaryDirectory
from pathlib import Path
from ..data.test_dict import test_dict
from latex_code_generation.code_generation import generate_meta_data_code


def test_latex_code_generation():
    output_dir = TemporaryDirectory()
    main_tex_path = Path(output_dir.name, 'main.tex')
    generate_meta_data_code(test_dict, Path(output_dir.name))

    assert main_tex_path.exists()
