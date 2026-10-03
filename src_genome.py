# genome.py - Executable genome: the digital DNA of an agent
#
# Each genome encodes behavioral traits + a style.
# It can mutate, cross, and generate a system prompt for an LLM.
#
# Author: alpha0az1omega
# License: MIT

import random
import json
import hashlib

# Genes and their (min, max) ranges
GENES = {
    "curiosity":    (0.0, 1.0),
    "caution":      (0.0, 1.0),
    "horizon":      (1, 3650),
    "aggressivity": (0.0, 1.0),
    "memory_size":  (8, 512),
    "risk_threshold": (0.0, 1.0),
}

STYLES = ["analytical", "narrative", "raw", "poetic"]


class Genome:
    """A digital genome. Deterministic identity via SHA-256."""

    def __init__(self, g=None, rng=None):
        self.rng = rng or random
        if g is None:
            self.g = {k: self.rng.uniform(lo, hi) for k, (lo, hi) in GENES.items()}
            self.g["style"] = self.rng.choice(STYLES)
        else:
            self.g = dict(g)
        self.id = self._hash()

    def _hash(self):
        """Deterministic identity: SHA-256 of the sorted genome."""
        raw = json.dumps(self.g, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()[:16]

    def muter(self, rate=0.15):
        """Return a mutated copy."""
        child = dict(self.g)
        for k, (lo, hi) in GENES.items():
            if self.rng.random() < rate:
                delta = self.rng.gauss(0, 0.15) * (hi - lo)
                child[k] = min(hi, max(lo, child[k] + delta))
        if self.rng.random() < rate:
            child["style"] = self.rng.choice(STYLES)
        return Genome(child, rng=self.rng)

    def croiser(self, other):
        """Return a crossover with another genome."""
        child = {k: self.rng.choice([self.g[k], other.g[k]]) for k in GENES}
        child["style"] = self.rng.choice([self.g["style"], other.g["style"]])
        return Genome(child, rng=self.rng)

    def prompt_systeme(self):
        """Generate a system prompt for an LLM from this genome."""
        g = self.g
        return (
            f"You are an autonomous agent. Style: {g['style']}. "
            f"Curiosity {g['curiosity']:.2f}, caution {g['caution']:.2f}, "
            f"aggressivity {g['aggressivity']:.2f}, horizon {int(g['horizon'])}d, "
            f"risk_threshold {g['risk_threshold']:.2f}, "
            f"memory {int(g['memory_size'])} items. "
            f"You reason step by step. You admit uncertainty."
        )

    def __repr__(self):
        return f"<Genome {self.id} style={self.g['style']}>"
