"""Dialog between the user and the shell, independent of the GUI."""

TAG_INPUT = "input"
TAG_OUTPUT = "output"
TAG_ERROR = "error"
TAG_DEBUG = "debug"


class Session:
    """Echoes commands, runs them and reports their results.

    All text is passed to the ``write(text, tag)`` callback, so the same
    logic serves the GUI window and the tests.
    """

    def __init__(self, shell, write):
        """Bind the session to a shell and an output callback."""
        self.shell = shell
        self.write = write

    def submit(self, line):
        """Run one command line as if the user had typed it.

        The prompt with the command and then its output are written.
        Returns the CommandResult of the command.
        """
        self.write(self.shell.prompt() + line, TAG_INPUT)
        result = self.shell.execute(line)
        if result.output:
            self.write(result.output, TAG_OUTPUT)
        if result.error:
            self.write(result.error, TAG_ERROR)
        return result
