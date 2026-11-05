"""Command interpreter of the emulator."""

from dataclasses import dataclass

from shell_emulator.parser import ParseError, parse_line

ROOT_PATH = "/"
DEFAULT_VFS_NAME = "default"


@dataclass
class CommandResult:
    """Result of executing one command line."""

    output: str = ""
    error: str = ""
    should_exit: bool = False


class Shell:
    """Parses and executes commands of the emulator."""

    def __init__(self, vfs_name=DEFAULT_VFS_NAME):
        """Create a shell working with the VFS named ``vfs_name``."""
        self.vfs_name = vfs_name
        self.cwd = ROOT_PATH
        self._commands = {
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "exit": self._cmd_exit,
        }

    def prompt(self):
        """Return the input prompt shown before each command."""
        return "{}:{}$ ".format(self.vfs_name, self.cwd)

    def execute(self, line):
        """Execute a command line and return a CommandResult."""
        try:
            tokens = parse_line(line)
        except ParseError as exc:
            return CommandResult(error="shell: syntax error: {}".format(exc))
        if not tokens:
            return CommandResult()
        name, args = tokens[0], tokens[1:]
        handler = self._commands.get(name)
        if handler is None:
            message = "shell: {}: command not found".format(name)
            return CommandResult(error=message)
        return handler(args)

    @staticmethod
    def _stub(name, args):
        """Build the output of a stub command: its name and arguments."""
        return CommandResult(output="{}: args = {!r}".format(name, args))

    def _cmd_ls(self, args):
        """Stub of the ``ls`` command."""
        return self._stub("ls", args)

    def _cmd_cd(self, args):
        """Stub of the ``cd`` command."""
        return self._stub("cd", args)

    @staticmethod
    def _cmd_exit(args):
        """Implementation of the ``exit`` command."""
        if args:
            return CommandResult(error="exit: too many arguments")
        return CommandResult(should_exit=True)
