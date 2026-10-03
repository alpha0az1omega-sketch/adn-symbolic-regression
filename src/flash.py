# flash.py - Symbolic regression in under 1 second
#
# Discovers mathematical formulas from numeric data.
# Runs on Android/Termux with only NumPy + SymPy + Rich.
#
# Author: alpha0az1omega
# License: MIT

import time, json, sys
from pathlib import Path
import numpy as np

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    console = Console()
    RICH = True
except ImportError:
    RICH = False

import journal

VERSION = "0.3.0-flash"


def build_library(X, var_names):
    """Build a library of candidate forms from input variables."""
    base = {}
    for i, n in enumerate(var_names):
        c = X[:, i]
        base[n]            = c
        base[f"{n}^2"]     = c ** 2
        base[f"{n}^3"]     = c ** 3
        base[f"1/{n}"]     = 1 / (c + 1e-6)
        base[f"1/{n}^2"]   = 1 / ((c + 1e-6) ** 2)
        base[f"sqrt({n})"] = np.sqrt(np.abs(c))
        base[f"sin({n})"]  = np.sin(c)
        base[f"cos({n})"]  = np.cos(c)
        base[f"exp(-{n})"] = np.exp(-np.abs(c))
        base[f"log({n})"]  = np.log(np.abs(c) + 1e-6)

    names = list(base.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            p = base[a] * base[b]
            if np.all(np.isfinite(p)) and np.std(p) < 1e6:
                base[f"({a})*({b})"] = p
    return base


def omp(Phi, y, k=5):
    """Orthogonal Matching Pursuit - pure NumPy."""
    n_feat = Phi.shape[1]
    residual = y.copy()
    selected = []
    coefs = np.zeros(n_feat)
    for _ in range(k):
        corr = Phi.T @ residual
        idx = int(np.argmax(np.abs(corr)))
        if idx in selected:
            break
        selected.append(idx)
        As = Phi[:, selected]
        c, *_ = np.linalg.lstsq(As, y, rcond=None)
        coefs[selected] = c
        residual = y - As @ c
    return coefs, selected


def normalize(Phi):
    """Normalize each column to unit norm."""
    norms = np.linalg.norm(Phi, axis=0)
    norms[norms < 1e-12] = 1.0
    return Phi / norms, norms


TARGETS = {
    "gravite":    {"vars": ["m1", "m2", "r"],
                   "f": lambda m1, m2, r: m1 * m2 / r**2,
                   "domaine": (0.5, 5.0),
                   "desc": "F = m1*m2/r^2"},
    "kepler":     {"vars": ["a"],
                   "f": lambda a: a ** 1.5,
                   "domaine": (0.5, 5.0),
                   "desc": "T = a^(3/2)"},
    "harmonique": {"vars": ["x"],
                   "f": lambda x: x * np.sin(x),
                   "domaine": (-3.0, 3.0),
                   "desc": "y = x*sin(x)"},
    "radioactif": {"vars": ["t"],
                   "f": lambda t: np.exp(-0.5 * t),
                   "domaine": (0.0, 6.0),
                   "desc": "N = exp(-t/2)"},
}


def run(target_name="gravite", seed=0):
    """Run symbolic regression on a named target."""
    tgt = TARGETS[target_name]
    rng = np.random.default_rng(seed)
    lo, hi = tgt["domaine"]
    n = 80
    X = rng.uniform(lo, hi, size=(n, len(tgt["vars"])))
    y = tgt["f"](*[X[:, i] for i in range(X.shape[1])])

    t0 = time.time()
    lib = build_library(X, tgt["vars"])
    names = list(lib.keys())
    Phi = np.column_stack([lib[nm] for nm in names])
    Phi_n, norms = normalize(Phi)
    y_scale = np.linalg.norm(y) or 1.0

    best = None
    for k in range(1, 7):
        coefs, sel = omp(Phi_n, y / y_scale, k=k)
        pred = Phi_n @ coefs * y_scale
        mse = float(np.mean((pred - y) ** 2))
        if best is None or mse < best[0]:
            best = (mse, k, coefs.copy(), sel)

    mse, k, coefs, sel = best
    real_coefs = coefs * y_scale / norms
    dt = time.time() - t0

    terms = []
    for idx in sel:
        c = real_coefs[idx]
        if abs(c) < 1e-8:
            continue
        terms.append(f"({c:+.4f})*{names[idx]}")
    formule = " ".join(terms)

    try:
        import sympy as sp
        sym_map = {v: sp.Symbol(v) for v in tgt["vars"]}
        expr = 0
        for idx in sel:
            c = real_coefs[idx]
            if abs(c) < 1e-8:
                continue
            nm = names[idx]
            local = dict(sym_map)
            try:
                e = eval(nm, {"__builtins__": {}}, {**local,
                    "sin": sp.sin, "cos": sp.cos, "exp": sp.exp,
                    "log": sp.log, "sqrt": sp.sqrt})
                expr += sp.Float(c) * e
            except Exception:
                pass
        expr_s = sp.sstr(sp.nsimplify(sp.simplify(expr), rational=False))
    except Exception:
        expr_s = formule

    conn = journal.init()
    run_id = journal.run_id_depuis(seed, f"{VERSION}:{target_name}", [])
    journal.demarrer_run(conn, run_id, seed, VERSION,
                         {"target": target_name, "n_features": len(names)})
    journal.log(conn, run_id, "flash", "discovery",
                {"mse": mse, "k": k, "formule": expr_s, "dt": dt})
    journal.terminer_run(conn, run_id)

    if RICH:
        console.print()
        console.print(Panel(
            f"[bold cyan]Target  [/] : {tgt['desc']}\n"
            f"[bold cyan]Formula [/] : [bold green]y = {expr_s}[/]\n"
            f"[bold cyan]MSE     [/] : {mse:.3e}\n"
            f"[bold cyan]Time    [/] : [bold yellow]{dt*1000:.1f} ms[/]\n"
            f"[bold cyan]run_id  [/] : {run_id}",
            title="[magenta]DISCOVERY FLASH[/]",
            border_style="magenta",
        ))
    else:
        print(f"Target: {tgt['desc']}")
        print(f"Formula: y = {expr_s}")
        print(f"MSE: {mse:.3e}")
        print(f"Time: {dt*1000:.1f} ms")

    out = Path.home() / "adn" / "runs" / run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "discovery.json").write_text(json.dumps({
        "run_id": run_id, "target": target_name,
        "formula": expr_s, "mse": mse, "dt_ms": dt * 1000,
        "library_size": len(names),
        "terms": [{"coef": float(real_coefs[i]), "name": names[i]} for i in sel],
    }, indent=2))

    return run_id, expr_s, mse


if __name__ == "__main__":
    for target in (sys.argv[1:] or ["kepler", "harmonique"]):
        if target in TARGETS:
            run(target)
            print()
