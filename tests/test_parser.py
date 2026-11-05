"""Tests of the command line parser."""

import unittest

from shell_emulator.parser import ParseError, parse_line


class ParseLineTest(unittest.TestCase):
    """Splitting of command lines into tokens."""

    def test_empty_line(self):
        """An empty or blank line gives no tokens."""
        self.assertEqual(parse_line(""), [])
        self.assertEqual(parse_line("   \t "), [])

    def test_split_by_spaces(self):
        """Tokens are separated by any amount of whitespace."""
        self.assertEqual(parse_line("ls  -l \t /home"), ["ls", "-l", "/home"])

    def test_double_quotes(self):
        """Double quotes group words into one argument."""
        self.assertEqual(
            parse_line('cd "My Documents"'), ["cd", "My Documents"]
        )

    def test_single_quotes(self):
        """Single quotes keep their content literally."""
        self.assertEqual(parse_line(r"ls 'a \n  b'"), ["ls", r"a \n  b"])

    def test_empty_quoted_argument(self):
        """An empty pair of quotes is an empty argument."""
        self.assertEqual(parse_line('ls "" x'), ["ls", "", "x"])

    def test_quotes_inside_word(self):
        """Quoted and unquoted parts of one word are glued together."""
        self.assertEqual(parse_line('ls ab"c d"e'), ["ls", "abc de"])

    def test_other_quote_inside_quotes(self):
        """A quote of another kind is an ordinary character."""
        line = """ls "it's" '"x"'"""
        self.assertEqual(parse_line(line), ["ls", "it's", '"x"'])

    def test_escapes(self):
        """A backslash escapes a space and a double quote."""
        self.assertEqual(parse_line(r"ls a\ b"), ["ls", "a b"])
        self.assertEqual(parse_line(r'ls "say \"hi\""'), ["ls", 'say "hi"'])

    def test_backslash_kept_in_double_quotes(self):
        """In double quotes a backslash before other characters stays."""
        self.assertEqual(parse_line(r'ls "a\nb"'), ["ls", r"a\nb"])

    def test_unterminated_quote(self):
        """A quote that is not closed is a parse error."""
        with self.assertRaises(ParseError):
            parse_line('ls "abc')
        with self.assertRaises(ParseError):
            parse_line("ls 'abc")

    def test_trailing_backslash(self):
        """A lone backslash at the end of the line is a parse error."""
        with self.assertRaises(ParseError):
            parse_line("ls abc\\")


if __name__ == "__main__":
    unittest.main()
