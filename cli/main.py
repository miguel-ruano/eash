import click
import cli as cli_module
from .core.command_template import CommandTemplate
from .core.assets_resolver import AssetsResolver
from .utils.files import read_file

GLOBAL_CONTEXT = {
    'CWD_PATH': cli_module.CWD_PATH,
    'OS_VERSION': cli_module.OS_TYPE
}
welcome_terminal = read_file(cli_module.root_file('__welcome__.txt'))
@click.group(help=click.style(welcome_terminal, fg='green'))
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug

assets_resolver = AssetsResolver(**cli_module.SETTINGS)
for command_path in assets_resolver.available_commands_paths:
    template = CommandTemplate.from_yml(command_path, GLOBAL_CONTEXT, assets_resolver)
    click_base = None
    if template.type == 'group':
        @cli.group(name=template.command, help=template.help)
        @click.pass_context
        def group_exec(*args, **kwargs):
            pass
        click_base = group_exec
    else:
        @cli.command(name=template.command, help=template.help)
        @click.pass_context
        def command_exec(*args, **kwargs):
            pass
        click_base = command_exec

    template.bind(click_base)


if __name__ == '__main__':
    cli()
