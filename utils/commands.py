import typing

from disnake import Option, Permissions

commands = []
groups = []
sub_commands = []
all_commands_classes = []


class Command:
    def __init__(self, *,
                 name: str,
                 desc: str,
                 options: typing.List[Option] = None,
                 perms: Permissions = Permissions.general(),
                 sub: list = None):
        self.name = name
        self.desc = desc
        self.options = options
        self.perms = perms
        self.sub = {cmd.name: cmd for cmd in sub} if sub is not None else None
        self.id = len(commands)

        if not isinstance(self, SubCommand) and not isinstance(self, SubCommandGroup):
            commands.append(self)
        all_commands_classes.append(self)

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.desc,
            'options': self.options
        }

    def sub_sort(self):
        """Сортировка всех подкоманд по имени"""
        if self.sub is not None:
            return sorted(self.sub.values(), key=lambda command: command.name)

    @staticmethod
    def sort():
        """Сортировка всех команд по имени"""
        return sorted(commands, key=lambda command: command.name)


class SubCommandGroup(Command):
    def __init__(self, *, name: str, sub: list):
        self.name = name
        self.sub = {cmd.name: cmd for cmd in sub} if sub is not None else None
        self.id = len(groups)

        groups.append(self)

    def to_dict(self):
        return {
            'name': self.name
        }


class SubCommand(Command):
    def __init__(self, *,
                 name: str,
                 desc: str,
                 options: typing.List[Option] = None,
                 perms: Permissions = Permissions.general()):
        super().__init__(name=name, desc=desc, options=options, perms=perms, sub=None)
        self.id = len(sub_commands)

        sub_commands.append(self)


def get_command(name: str):
    try:
        return list(filter(lambda command: command.name == name, all_commands_classes))[0]
    except IndexError:
        return False
