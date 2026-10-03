# main.py - Reproducibility test
#
# Verifies the engine is deterministic:
#   - Same seed -> same run_id
#   - Same seed -> same trajectory
#   - Different seeds -> different run_id
#
# Author: alpha0az1omega
# License: MIT

import random
import hashlib
import json
import sys
import os

# Ensure we can import local modules (genome, journal)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genome import Genome
import journal

VERSION = "0.1.0"


def executer(seed, pop_size=20, generations=10, verbose=True):
    """Run one genetic experiment with a given seed."""
    rng = random.Random(seed)
    conn = journal.init()

    pop_init = [Genome(rng=rng) for _ in range(pop_size)]
    run_id = journal.run_id_depuis(seed, VERSION, pop_init)
    journal.demarrer_run(conn, run_id, seed, VERSION,
                         {"pop": pop_size, "gen": generations})

    pop = pop_init
    trajectory = []
    for gen in range(generations):
        scores = [(g, rng.random()) for g in pop]
        scores.sort(key=lambda x: -x[1])
        top = [(g.id, round(s, 4)) for g, s in scores[:5]]
        trajectory.append(top)
        journal.log(conn, run_id, "population", "fitness", top)

        elites = [g for g, _ in scores[:pop_size // 4]]
        new_pop = list(elites)
        while len(new_pop) < pop_size:
            if rng.random() < 0.6:
                new_pop.append(rng.choice(elites).muter())
            else:
                a, b = rng.choice(elites), rng.choice(elites)
                new_pop.append(a.croiser(b))
        pop = new_pop

    journal.terminer_run(conn, run_id)
    fingerprint = hashlib.sha256(
        json.dumps(trajectory, sort_keys=True).encode()
    ).hexdigest()[:16]

    if verbose:
        print(f"seed={seed} run_id={run_id} fingerprint={fingerprint}")

    return run_id, fingerprint


if __name__ == "__main__":
    print("=== Run 1 (seed 42) ===")
    r1, e1 = executer(42)

    print("=== Run 2 (seed 42) ===")
    r2, e2 = executer(42)

    print("=== Run 3 (seed 43) ===")
    r3, e3 = executer(43)

    # Reproducibility assertions
    assert r1 == r2, "FAIL: same seed should give same run_id"
    assert e1 == e2, "FAIL: same seed should give same trajectory"
    assert r1 != r3, "FAIL: different seeds should diverge"

    print()
    print("OK - Reproducibility verified. The world is stable.")
