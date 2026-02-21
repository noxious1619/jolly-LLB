# conftest.py — pytest configuration for JOLLY-LLB
# Ensures the project root is always on sys.path so both
# `tests/` (the dedicated test folder) and root-level test
# files can import app/, logic/, scripts/, agents/ and api/
# without any prefix path issues.

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(__file__))
