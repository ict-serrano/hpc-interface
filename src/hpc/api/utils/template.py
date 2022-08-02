from jinja2 import Environment, PackageLoader, select_autoescape

def render(hpc_service_params):
    env = Environment(
        loader=PackageLoader("hpc"),
        autoescape=select_autoescape()
    )
    template = env.get_template("exe.sh.j2")
    return template.render(params=hpc_service_params)