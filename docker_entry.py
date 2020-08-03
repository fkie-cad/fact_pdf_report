#!/usr/bin/env python3
'''
    fact_pdf_report
    Copyright (C) 2015-2019  Fraunhofer FKIE

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import json
import shutil
from pathlib import Path
from sys import exit as sys_exit
from tempfile import TemporaryDirectory

from pdf_generator.generator import compile_pdf, create_templates


def get_data():
    return json.loads(Path('/tmp', 'interface', 'data', 'analysis.json').read_text()), json.loads(
        Path('/tmp', 'interface', 'data', 'meta.json').read_text())


def move_pdf_report(pdf_path):
    shutil.move(str(pdf_path.absolute()), str(Path('/tmp', 'interface', 'pdf', pdf_path.name)))


def main(template_style='default'):
    analysis, meta_data = get_data()

    with TemporaryDirectory() as tmp_dir:
        create_templates(analysis, meta_data, tmp_dir, template_style)
        try:
            target_path = compile_pdf(meta_data, tmp_dir)
            move_pdf_report(target_path)
        except RuntimeError:
            pass

    return 0


if __name__ == '__main__':
    sys_exit(main())
