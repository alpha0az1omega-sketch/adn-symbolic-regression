# journal.py - Append-only journal with reproducible provenance
#
# Every run is written to an SQLite database in append-only mode.
# A run_id is deterministically derived from (seed, version, genomes).
#
# Author: alpha0az1omega
# License: MIT

import sqlite3
import json
import hashlib
import time
from pathlib import Path

# Database location (in ~/adn/journal.db)
DB = Path.home() / "adn" / "journal.db"
DB.parent.mkdir(parents=True, exist_ok=True)


def init():
    """Open the database and create tables if needed."""
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS evenements(
        t REAL, run_id TEXT, agent_id TEXT, type TEXT,
        contenu TEXT, hash TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS runs(
        run_id TEXT PRIMARY KEY, seed INTEGER, version TEXT,
        t_debut REAL, t_fin REAL, meta TEXT)""")
    c.commit()
    return c


def run_id_depuis(seed, version, genomes_init):
    """Compute a deterministic run_id from seed + version + genomes."""
    ids = sorted(g.id for g in genomes_init)
    raw = f"{seed}|{version}|{','.join(ids)}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def demarrer_run(conn, run_id, seed, version, meta=None):
    """Register the start of a run."""
    conn.execute(
        "INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?)",
        (run_id, seed, version, time.time(), None, json.dumps(meta or {})),
    )
    conn.commit()


def terminer_run(conn, run_id):
    """Register the end of a run."""
    conn.execute(
        "UPDATE runs SET t_fin=? WHERE run_id=?",
        (time.time(), run_id)
    )
    conn.commit()


def log(conn, run_id, agent_id, type_, contenu):
    """Append an event to the journal (never deleted)."""
    t = time.time()
    payload = json.dumps(contenu, sort_keys=True, default=str)
    h = hashlib.sha256((str(t) + run_id + payload).encode()).hexdigest()[:16]
    conn.execute(
        "INSERT INTO evenements VALUES (?,?,?,?,?,?)",
        (t, run_id, agent_id, type_, payload, h)
    )
    conn.commit()
    return h


def compter_runs(conn):
    """Return the number of runs recorded."""
    cur = conn.execute("SELECT COUNT(*) FROM runs")
    return cur.fetchone()[0]


def compter_evenements(conn):
    """Return the number of events recorded."""
    cur = conn.execute("SELECT COUNT(*) FROM evenements")
    return cur.fetchone()[0]
