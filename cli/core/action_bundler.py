import re
import os
import cli
import subprocess
from cli.utils.expressions import parse_expressions
from cli.utils.files import create_dir, create_file, copy_files, remove_dir

REGEX_EXPRESS = r"(?:(MKFILE) (.*)\n`{3}\n((?:.|\n)*?)(?<!\\)`{3}\n?)"
REGEX_EXPRESS += r"|(?:(MKDIR) (.*))"
REGEX_EXPRESS += r"|(?:(RMDIR) (.*))"
REGEX_EXPRESS += r"|(?:(RUN) (.*?) '(.*)')"
REGEX_EXPRESS += r"|(?:(CP) '(.*?)' '(.*?)'[ ]?(.*))"
REGEX_EXPRESS += r"|(?:(WORKDIR) (.*))"
REGEX_EXPRESS_COMPILE = re.compile(REGEX_EXPRESS, re.MULTILINE)

ACTIONS_MAPPER = {
    'MKFILE': lambda self, action: ({
        'logger': self.log,
        'action': action[0],
        'file_path': os.path.join(self.__dir_root_path__, self.__parse_expression__(action[1])),
        'content': self.__parse_expression__(action[2])
    }),
    'MKDIR': lambda self, action: ({
        'logger': self.log,
        'action': action[0],
        'dir_path': os.path.join(self.__dir_root_path__, self.__parse_expression__(action[1]))
    }),
    'RMDIR': lambda self, action: ({
        'logger': self.log,
        'action': action[0],
        'dir': self.__parse_expression__(action[1]),
    }),
    'RUN': lambda self, action: ({
        'logger': self.log,
        'action': action[0],
        'command': self.__parse_expression__(action[2]),
        'context': self.__parse_expression__(action[1])
    }),
    'CP': lambda self, action: ({
        'logger': self.log,
        'action': action[0],
        'src': self.__parse_expression__(action[1]),
        'dst': self.__parse_expression__(action[2]),
        'opts': self.__parse_expression__(action[3])
    }),
    'WORKDIR': lambda self, action: ({
        'logger': self.log,
        'action': action[0],
        'dir_path': os.path.join(self.__dir_root_path__, self.__parse_expression__(action[1])),
        'exec_now': True
    })
}


def exec_bash(self, action, current_dir: str):
    dir = self.__parse_expression__(
        action['context']) if 'context' in action else current_dir
    dir = current_dir if dir == '.' else dir
    command = self.__parse_expression__(action['command'])
    result = subprocess.check_output(command, shell=True, text=True, cwd=dir)
    if action['logger']:
        print(str(result))


ACTIONS_EXECUTE_MAPPER = {
    'MKFILE': lambda self, action, ctx: create_file(action['file_path'], action['content']),
    'MKDIR': lambda self, action, ctx: create_dir(action['dir_path']),
    'RMDIR': lambda self, action, ctx: remove_dir(os.path.join(self.__dir_root_path__, action['dir'])),
    'WORKDIR': lambda self, action, ctx: self.turn_workdir(action['dir_path']),
    'RUN': lambda self, action, ctx: exec_bash(self, action, self.__dir_root_path__),
    'CP': lambda self, action, ctx: copy_files(self.__dir_root_path__, action['dst'], action['src'], opts= action['opts'])
}


class ActionBundler():

    def __init__(self, bundler: str, context: dict = None, log: bool = True) -> None:
        self.bundler = bundler
        self.context = context
        self.log = log
        self.context['WORK_DIR'] = self.__dir_root_path__
        self.__load_actions__()

    def __load_actions__(self):
        actions = list(
            map(lambda f: tuple(filter(lambda v: v != None, f.groups())),
                REGEX_EXPRESS_COMPILE.finditer(self.bundler))
        )
        self.actions = []
        for action in actions:
            action_key = action[0]
            if action_key in ACTIONS_MAPPER:
                action_map = ACTIONS_MAPPER[action_key](self, action)
                exec_now = action_map['exec_now'] if 'exec_now' in action_map else False
                if exec_now:
                    self.__exec_action__(action_map)
                else:
                    self.actions.append(action_map)

    def execute(self):
        for action in self.actions:
            self.__exec_action__(action)

    def turn_workdir(self, new_workdir):
        self.context["WORK_DIR"] = os.path.join(
            self.__dir_root_path__, self.__parse_expression__(new_workdir))

    def __exec_action__(self, action):
        action_key = action['action']
        handler = ACTIONS_EXECUTE_MAPPER[action_key
                                         ] if action_key in ACTIONS_EXECUTE_MAPPER else None
        if handler:
            handler(self, action, self.context)

    def __parse_expression__(self, expression):
        return parse_expressions(expression, self.context)

    @property
    def __dir_root_path__(self):
        return self.context['WORK_DIR'] if 'WORK_DIR' in self.context else cli.CWD_PATH

    @staticmethod
    def load_from_file(file_path: str, context: dict = None, log: bool = True):
        with open(file_path, 'r') as file:
            return ActionBundler(file.read(), context, log)
