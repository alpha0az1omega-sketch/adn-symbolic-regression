# tests/test_reproducibility.py
#
# Tests that the engine is deterministic.
# Run with: python test_reproducibility.py
#
# Author: alpha0az1omega
# License: MIT

import sys
import os

# Add src/ to import path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

import main


def test_same_seed_same_run():
    """Same seed must produce the same run_id."""
    r1, _ = main.executer(42, verbose=False)
    r2, _ = main.executer(42, verbose=False)
    assert r1 == r2, f"Same seed gave different run_id: {r1} vs {r2}"
    print("  OK: same seed -> same run_id")


def test_same_seed_same_fingerprint():
    """Same seed must produce the same trajectory fingerprint."""
    _, e1 = main.executer(42, verbose=False)
    _, e2 = main.executer(42, verbose=False)
    assert e1 == e2, f"Same seed gave different fingerprint: {e1} vs {e2}"
    print("  OK: same seed -> same trajectory")


def test_different_seed_diverges():
    """Different seeds must produce different run_ids."""
    r1, _ = main.executer(42, verbose=False)
    r3, _ = main.executer(43, verbose=False)
    assert r1 != r3, "Different seeds gave the same run_id"
    print("  OK: different seeds -> different run_id")


if __name__ == "__main__":
    print("Running reproducibility tests...")
    print()
    test_same_seed_same_run()
    test_same_seed_same_fingerprint()
    test_different_seed_diverges()
    print()
    print("All tests passed.")
