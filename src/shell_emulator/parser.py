"""Command line parser with support for quoted arguments."""

SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKSLASH = "\\"
QUOTES = (SINGLE_QUOTE, DOUBLE_QUOTE)
ESCAPABLE_IN_DOUBLE = (DOUBLE_QUOTE, BACKSLASH)


class ParseError(ValueError):
    """Raised when a command line cannot be split into tokens."""


class _Tokenizer:
    """State machine that splits a command line into tokens."""

    def __init__(self):
        """Create a tokenizer in its initial state."""
        self.tokens = []
        self.chars = []
        self.has_token = False
        self.quote = ""
        self.escaped = False

    def feed(self, char):
        """Process a single character of the command line."""
        if self.escaped:
            self._finish_escape(char)
        elif char == BACKSLASH and self.quote != SINGLE_QUOTE:
            self.escaped = True
            self.has_token = True
        elif self.quote:
            self._feed_quoted(char)
        elif char in QUOTES:
            self.quote = char
            self.has_token = True
        elif char.isspace():
            self._flush()
        else:
            self.chars.append(char)
            self.has_token = True

    def finish(self):
        """Finish parsing and return the list of tokens."""
        if self.quote:
            raise ParseError("unterminated quote: " + self.quote)
        if self.escaped:
            raise ParseError("trailing backslash")
        self._flush()
        return self.tokens

    def _feed_quoted(self, char):
        """Process a character located inside quotes."""
        if char == self.quote:
            self.quote = ""
        else:
            self.chars.append(char)

    def _finish_escape(self, char):
        """Process the character that follows a backslash."""
        keeps_backslash = (
            self.quote == DOUBLE_QUOTE and char not in ESCAPABLE_IN_DOUBLE
        )
        if keeps_backslash:
            self.chars.append(BACKSLASH)
        self.chars.append(char)
        self.escaped = False

    def _flush(self):
        """Store the accumulated token, if there is one."""
        if self.has_token:
            self.tokens.append("".join(self.chars))
        self.chars = []
        self.has_token = False


def parse_line(line):
    """Split a command line into a list of tokens.

    Tokens are separated by whitespace. Single quotes keep their content
    literally, double quotes allow the escapes ``\\"`` and ``\\\\``, and
    a backslash outside quotes escapes the next character. An empty
    quoted string produces an empty token.

    Raises ParseError if a quote is not closed or the line ends with
    a lone backslash.
    """
    tokenizer = _Tokenizer()
    for char in line:
        tokenizer.feed(char)
    return tokenizer.finish()
