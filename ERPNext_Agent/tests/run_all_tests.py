"""Master Test Runner for ERPNext AI Agent."""

import os
import sys
import unittest

# Ensure the root directory is on Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def run_suite():
	tests_dir = os.path.dirname(os.path.abspath(__file__))
	loader = unittest.TestLoader()
	suite = loader.discover(start_dir=tests_dir, pattern="test_*.py")
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)
	sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
	run_suite()
