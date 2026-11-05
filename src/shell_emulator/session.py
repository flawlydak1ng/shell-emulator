"""Dialog between the user and the shell, independent of the GUI."""

from dataclasses import dataclass

TAG_INPUT = "input"
TAG_OUTPUT = "output"
TAG_ERROR = "error"
TAG_DEBUG = "debug"
SCRIPT_ENCODING = "utf-8-sig"


@dataclass
class ScriptReport:
    """Summary of a startup script run."""

    executed: int = 0
    skipped: int = 0
    exited: bool = False


class Session:
    """Echoes commands, runs them and reports their results.

    All text is passed to the ``write(text, tag)`` callback, so the same
    logic serves the GUI window and the tests.
    """

    def __init__(self, shell, write, on_result=None):
        """Bind the session to a shell and an output callback.

        The optional ``on_result(result)`` callback is called after every
        command, for example to refresh the prompt or to close the window.
        """
        self.shell = shell
        self.write = write
        self.on_result = on_result

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
        if self.on_result:
            self.on_result(result)
        return result

    def run_script(self, path):
        """Run a startup script, showing both its input and its output.

        Commands are executed one after another. Blank lines are ignored,
        lines that end with an error are skipped (the error is shown and
        the script goes on). The ``exit`` command stops the script.
        Returns a ScriptReport.
        """
        report = ScriptReport()
        try:
            lines = read_script(path)
        except (OSError, UnicodeDecodeError) as exc:
            self.write("script: cannot read {}: {}".format(path, exc),
                       TAG_ERROR)
            return report
        for line in lines:
            if not line.strip():
                continue
            result = self.submit(line)
            if result.should_exit:
                report.exited = True
                break
            report.executed += 1
            report.skipped += bool(result.error)
        return report


def read_script(path):
    """Read a script file and return its lines without line breaks."""
    with open(path, encoding=SCRIPT_ENCODING) as script:
        return script.read().splitlines()
