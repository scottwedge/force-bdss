import unittest
import subprocess
import os
from contextlib import contextmanager

from force_bdss.tests import fixtures


@contextmanager
def cd(dir):
    cwd = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(cwd)


def fixture_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "fixtures")


class TestExecution(unittest.TestCase):
    def test_plain_invocation_mco(self):
        with cd(fixtures.dirpath()):
            try:
                subprocess.check_output(["force_bdss", "test_empty.json"])
            except subprocess.CalledProcessError:
                self.fail("force_bdss returned error at plain invocation.")

    def test_plain_invocation_evaluate(self):
        with cd(fixtures.dirpath()):
            proc = subprocess.Popen([
                "force_bdss", "--evaluate", "test_empty.json"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            proc.communicate(b"1")
            retcode = proc.wait()
            self.assertEqual(retcode, 0)

    def test_unsupported_file_input(self):
        with cd(fixtures.dirpath()):
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_output(
                    ["force_bdss", "test_csv_v2.json"],
                    stderr=subprocess.STDOUT)

    def test_corrupted_file_input(self):
        with cd(fixtures.dirpath()):
            with self.assertRaises(subprocess.CalledProcessError):
                subprocess.check_output(
                    ["force_bdss", "test_csv_corrupted.json"],
                    stderr=subprocess.STDOUT)


if __name__ == '__main__':
    unittest.main()
