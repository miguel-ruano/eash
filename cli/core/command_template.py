import yaml
from cli.core.assets_resolver import AssetsResolver
import click

from .command_template_step import CommandTemplateStep
from cli.utils.class_utils import load_class
from cli.utils.expressions import parse_expressions
from cli import OS_TYPE

COMMAND_PROPS = ['command', 'options', 'arguments', 'showStepsLog',
                 'commands', 'type', 'steps', 'help', 'endMessage']


class CommandTemplate(object):

    def __init__(self, context: dict = None, assets_resolver: AssetsResolver = AssetsResolver(), **kwargs) -> None:
        self.data = kwargs
        self.context = context
        self.assets_resolver = assets_resolver

    def __getattribute__(self, __name: str):
        __data__ = super().__getattribute__('data')
        return (__data__[__name] if __name in __data__ else None) if __name in COMMAND_PROPS else super().__getattribute__(__name)

    def bind(self, command: click.Command):
        self.bind_options(command)
        self.bind_arguments(command)
        self.bind_commands(command)
        command.callback = self.__command__

    def bind_options(self, command: click.Command):
        if not self.options:
            return None
        for param in self.options:
            required = bool(param['required']
                            ) if 'required' in param else False
            default = param['default'] if 'default' in param else None
            if default:
                default = self.__parse_expression(default)
            command.params.append(
                click.Option([self.__option_alias(param['name'])], prompt=required, show_default=True,
                             help=param['help'] if 'help' in param else '', type=self.__param_type(param), default=default)
            )

    def bind_arguments(self, command: click.Command):
        if not self.arguments:
            return None
        for param in self.arguments:
            required = bool(param['required']
                            ) if 'required' in param else False
            default = param['default'] if 'default' in param else None
            if default:
                default = self.__parse_expression(default)
            command.params.append(
                click.Argument([param['name']], default = default,
                               required=required, type=self.__param_type(param))
            )

    def bind_commands(self, group: click.Group):
        if not self.commands and self.type != 'group':
            return None
        for command in self.commands:
            template = CommandTemplate(
                self.context, self.assets_resolver, **command)

            @group.command(name=template.command, help=template.help)
            @click.pass_context
            def command_exec(*args, **kargs):
                pass
            template.bind(command_exec)

    def __parse_expression(self, expression, context: dict = {}):
        return parse_expressions(expression, {**self.context, **context})

    def __option_alias(self, option_alias):
        return f'--{option_alias}'

    def __param_type(self, param):
        __type = param['type'] if 'type' in param else 'str'
        if __type == 'choice':
            return click.Choice(param['options'] if 'options' in param else [])
        else:
            return load_class(f"builtins.{__type}")

    def __command__(self, *args, **kwargs):
        try:
            self.__exec_steps__(**kwargs)
            if self.endMessage:
                click.echo(click.style(self.endMessage, bold=True))
        except Exception as e:
            click.echo(f'Se ha presentado un error: {str(e)}', err=True)
            raise e

    def __exec_steps__(self, *args, **kwargs):
        if not self.steps:
            return None
        showStepsLog = self.showStepsLog == True or self.showStepsLog == None
        steps = list(
            filter(
                lambda step: 'os' not in step or step['os'] == OS_TYPE, self.steps)
        )
        step_len = len(steps)
        for idx, step in enumerate(steps):
            step['log'] = step['log'] if 'log' in step else True if showStepsLog else False
            step_wrapper = CommandTemplateStep(step, self.assets_resolver)
            if showStepsLog:
                message = step['message'] if 'message' in step else ''
                click.echo(click.style(
                    f'PASO {idx+1} de {step_len} {message}...', bold=True))
            step_wrapper.exec({
                **self.context,
                **kwargs
            })
            if step_wrapper.stop_on_exec:
                break

    @staticmethod
    def from_yml(yml_path, context: dict = None, assets_resolver: AssetsResolver = AssetsResolver()):
        with open(yml_path, 'r') as yml_file:
            yml_data = yaml.load(yml_file, Loader=yaml.FullLoader)
            return CommandTemplate(context=context, assets_resolver=assets_resolver, **yml_data)
