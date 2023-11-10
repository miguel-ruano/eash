import os

from cli import root_file
from cli.utils.files import exists_file, list_files
from .action_bundler import ActionBundler


class AssetsResolver():

    def __init__(self, commands: str = None, bundlers: str = None, **kwargs) -> None:
        self.__list__commands_paths__ = None
        self.commands = [root_file('assets/commands')]
        if commands:
            self.commands.append(commands)
        self.bundlers = [root_file('assets/bundlers')]
        if bundlers:
            self.bundlers.append(bundlers)

    @property
    def available_commands_paths(self) -> list:
        if not self.__list__commands_paths__:
            self.__list__commands_paths__ = []
            for command_dir in self.commands:
                if exists_file(command_dir):
                    self.__list__commands_paths__ += list_files(command_dir)
        return self.__list__commands_paths__

    def resolve_bundler_path(self, bundler_path: str) -> str:
        for bundler_dir in self.bundlers:
            f_bundler_path = os.path.join(bundler_dir, bundler_path)
            if exists_file(os.path.join(bundler_dir, bundler_path)):
                return f_bundler_path
        return None

    def exists_bundler(self, bundler_path: str) -> bool:
        f_bundler_path = self.resolve_bundler_path(bundler_path)
        return f_bundler_path != None

    def load_bundler(self, bundler_path: str, ctx: dict, log: bool = True):
        f_bundler_path = self.resolve_bundler_path(bundler_path)
        if f_bundler_path:
            return ActionBundler.load_from_file(f_bundler_path, ctx, log)
        return None
