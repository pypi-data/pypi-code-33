import argparse
import unittest

from slack_invoker import parse

class TestWrapRunner(unittest.TestCase):
    def setUp(self):
        def runner(a, b, c=1):
            return (a, b, c)
        self.runner = runner

        # Parser which parses exactly the arguments required by the runner
        # in which the defaults are consistent with runner defaults.
        self.good_consistent_parser = argparse.ArgumentParser('Good, consistent parser')
        self.good_consistent_parser.add_argument('-a', required=True)
        self.good_consistent_parser.add_argument('-b', required=True)
        self.good_consistent_parser.add_argument('-c', type=int, default=1)

        # Parser which parses exactly the arguments required by the runner
        # in which the defaults are inconsistent with runner defaults.
        self.good_inconsistent_parser = argparse.ArgumentParser('Good, inconsistent parser')
        self.good_inconsistent_parser.add_argument('-a', required=True)
        self.good_inconsistent_parser.add_argument('-b', required=True)
        self.good_inconsistent_parser.add_argument('-c', type=int, default=42)

        # Parser which parses arguments not expected by the runner
        self.bad_parser = argparse.ArgumentParser('Bad parser')
        self.bad_parser.add_argument('-a', required=True)
        self.bad_parser.add_argument('-b', required=True)
        self.bad_parser.add_argument('-c', type=int, default=42)
        self.bad_parser.add_argument('-d')

    def test_wrap_runner_good_consistent_parser_help(self):
        wrapped_runner = parse.wrap_runner(self.good_consistent_parser, self.runner)
        result = wrapped_runner(['-a', 'lol', '-b', 'rofl', '-c', '2', '-h'])
        self.assertEqual(result, '```{}```'.format(self.good_consistent_parser.format_help()))

    def test_wrap_runner_good_consistent_parser_1(self):
        wrapped_runner = parse.wrap_runner(self.good_consistent_parser, self.runner)
        result = wrapped_runner(['-a', 'lol', '-b', 'rofl', '-c', '2'])
        self.assertTupleEqual(result, ('lol', 'rofl', 2))

    def test_wrap_runner_good_consistent_parser_2(self):
        wrapped_runner = parse.wrap_runner(self.good_consistent_parser, self.runner)
        result = wrapped_runner(['-a', 'lol', '-b', 'rofl'])
        self.assertTupleEqual(result, ('lol', 'rofl', 1))

    def test_wrap_runner_good_consistent_parser_3(self):
        wrapped_runner = parse.wrap_runner(self.good_consistent_parser, self.runner)
        result = wrapped_runner('-a "lol lol" -b rofl -c 2')
        self.assertTupleEqual(result, ('lol lol', 'rofl', 2))

    def test_wrap_runner_good_consistent_parser_4(self):
        wrapped_runner = parse.wrap_runner(self.good_consistent_parser, self.runner)
        with self.assertRaises(parse.ParseError):
            wrapped_runner('-a "lol lol" -c 2')

    def test_wrap_runner_good_inconsistent_parser_1(self):
        wrapped_runner = parse.wrap_runner(self.good_inconsistent_parser, self.runner)
        result = wrapped_runner(['-a', 'lol', '-b', 'rofl', '-c', '2'])
        self.assertTupleEqual(result, ('lol', 'rofl', 2))

    def test_wrap_runner_good_inconsistent_parser_2(self):
        wrapped_runner = parse.wrap_runner(self.good_inconsistent_parser, self.runner)
        result = wrapped_runner(['-a', 'lol', '-b', 'rofl'])
        self.assertTupleEqual(result, ('lol', 'rofl', 42))

    def test_wrap_runner_bad_parser_1(self):
        wrapped_runner = parse.wrap_runner(self.bad_parser, self.runner)
        with self.assertRaises(TypeError):
            wrapped_runner(['-a', 'lol', '-b', 'rofl', '-c', '2', '-d', 'wtf'])

class TestSlackEmailParser(unittest.TestCase):
    def test_well_formed_slack_email(self):
        email_address = 'sixpack@example.com'
        slack_email_string = '<mailto:{}|Joe Sixpack>'.format(email_address)
        parsed_email = parse.slack_email(slack_email_string)
        self.assertEqual(parsed_email, email_address)

    def test_ill_formed_slack_email(self):
        slack_email_string = 'lol'
        with self.assertRaises(Exception):
            parse.slack_email(slack_email_string)

    def test_raw_email_address(self):
        slack_email_string = 'sixpack@example.com'
        with self.assertRaises(Exception):
            parse.slack_email(slack_email_string)
