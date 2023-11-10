import click
from .core_fn import eval_context
from cli.core.assets_resolver import AssetsResolver
from cli.utils.expressions import parse_expressions
from .action_bundler import ActionBundler


class CommandTemplateStep(object):

    STEP_EXEC = {
        'bundler-action': lambda self, ctx: self.__step_bundler_action__(ctx),
        'bundler-action-inline': lambda self, ctx: self.__step_bundler_action_inline__(ctx),
        'command': lambda self, ctx: self.__step_exec_command__(ctx),
        'eval': lambda self, ctx: self.__step_eval_expression__(ctx)
    }

    def __init__(self, step, assets_resolver: AssetsResolver):
        self.step = step
        self.assets_resolver = assets_resolver

    @property
    def stop_on_exec(self):
        return bool(self.step['stop']) if 'stop' in self.step else False

    @property
    def message(self):
        return self.step['message'] if 'message' in self.step else ''

    def exec(self, context: dict):
        step_context = self.__step_vars__(context)
        fcontext = {**context, **step_context}
        continue_exec = self.can_exec(fcontext)
        if continue_exec:
            self.__exec__(fcontext)

    def can_exec(self, context: dict) -> bool:
        condition_expression = self.step['condition'] if 'condition' in self.step else None
        continue_step = condition_expression is None or self.__eval_expression__(
            condition_expression, context)
        return continue_step

    def __exec__(self, context):
        if self.step['type'] in CommandTemplateStep.STEP_EXEC:
            __exec__ = CommandTemplateStep.STEP_EXEC[self.step['type']]
            __exec__(self, context)

    def __step_vars__(self, args: dict):
        vars = self.step['vars'] if 'vars' in self.step else {}
        step_vars = {}
        for var in vars:
            context_var, args_var = var.split(':')
            args_var = parse_expressions(args_var, args)
            step_vars[context_var] = args_var
        return step_vars

    def __eval_expression__(self, expression, context: dict = {}):
        context = {
            **context
        }
        return eval(expression, context)

    def __step_bundler_action__(self, context):
        bundlers = self.step['bundler']
        for bundler_path in bundlers:
            bundler = self.assets_resolver.load_bundler(
                bundler_path, context, self.step['log'])
            if bundler:
                bundler.execute()
            else:
                raise Exception(
                    f'bundler file "{bundler_path}" not found in bundler dirs: {self.bundlers}')

    def __step_bundler_action_inline__(self, context):
        dir = parse_expressions(
            self.step['context'], context) if 'context' in self.step else '.'
        action = parse_expressions(self.step['action'], context)
        ActionBundler(action, {
                      **context, 'WORK_DIR': dir}, self.step['log']).execute()

    def __step_exec_command__(self, context):
        dir = parse_expressions(
            self.step['context'], context) if 'context' in self.step else '.'
        command = parse_expressions(self.step['command'], context)
        ActionBundler(f"RUN {dir} '{command}'", {
                      **context, 'WORK_DIR': dir}, self.step['log']).execute()

    def __step_eval_expression__(self, context):
        context = eval_context(context)
        eval = parse_expressions(self.step['eval'], context)
        result = self.__eval_expression__(eval, context)
        if result:
            click.echo(result if result else 'Sin valor')
        elif (self.step['emptyMessage'] if 'emptyMessage' in self.step else None):
            click.echo(self.step['emptyMessage'])
