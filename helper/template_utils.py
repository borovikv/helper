import helper.settings as settings


def get_template(template_name):
    from jinja2 import Environment, FileSystemLoader
    return Environment(loader=FileSystemLoader(settings.TEMPLATE_PATH)).get_template(template_name)


def render_to_response(template, context):
    template = get_template(template)
    return template.render(**context)
