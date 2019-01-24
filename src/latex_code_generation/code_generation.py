import jinja2
from pathlib import Path


def generate_code(analysis_dict, output_path):
    jinja_env = _set_jinja_env()


def _set_jinja_env(templates_to_use='default'):
    template_directory = Path(Path(__file__).parent.parent, 'templates', templates_to_use)
    return jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(str(template_directory))
    )


def _render_template(data, jinja_env, template):
    output = jinja_env.get_template('{}.tex'.format(template))
    return output.render(analysis=data['analysis'], meta_data=data['meta_data'])


def _write_file(raw_data, file_path):
    with open(file_path, 'w') as fp:
        fp.write(raw_data)
